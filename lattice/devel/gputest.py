import pycuda.driver as cuda
import pycuda.compiler
import pycuda.gpuarray as gpuarray
import pycuda.autoinit
import pycuda.curandom
from pycuda.compiler import SourceModule

import numpy as np

code = """
    #include <curand_kernel.h>

    extern "C"
    {
    #define CURAND_CALL ( x ) do { if (( x ) != CURAND_STATUS_SUCCESS ) {\
    printf (" Error at % s :% d \ n " , __FILE__ , __LINE__ ) ;\
    return EXIT_FAILURE ;}} while (0)

    __global__ void setup_kernel (int nthreads, curandState *state, unsigned long long seed, unsigned long long offset)
    {
        /* Thanks to Anthony LaTorre */
        int id = blockIdx.x*blockDim.x + threadIdx.x;

        if (id >= nthreads)
            return;
        /* Each thread gets same seed, a different sequence number, no offset */
        curand_init (seed, id, offset, &state[id]);
    }


    __global__ void sim_drift(curandState *global_state, float const v, float const V, float const a, float const z, float const Z, float const t, float const T, float const dt, float const intra_sv, float *out)
    {
        float start_delay, start_point, drift_rate, rand, prob_up, position, step_size, time;
        int idx = blockIdx.x*blockDim.x + threadIdx.x;

        curandState local_state = global_state[idx];

        /* Sample variability parameters. */
        start_delay = curand_uniform(&local_state)*T + (t-T/2);
        start_point = (curand_uniform(&local_state)*Z + (z-Z/2))*a;
        drift_rate = curand_normal(&local_state)*V + v;

        /* Set up drift variables. */
        prob_up = .5f*(1+sqrtf(dt)/intra_sv*drift_rate);
        step_size = sqrtf(dt)*intra_sv;
        time = start_delay;
        position = start_point;

        /* Simulate particle movement until threshold is crossed. */
        while (position > 0 & position < a) {
            rand = curand_uniform(&local_state);
            position += ((rand < prob_up)*2 - 1) * step_size;
            time += dt;
        }

        /* Save back state. */
        global_state[idx] = local_state;

        /* Figure out boundary, save result. */
        if (position <= 0) {
            out[idx] = -time;
        }
        else {
            out[idx] = time;
        }
    }

    __global__ void sim_drift_var_thresh(curandState *global_state, float const v, float const V, float const *a, float const z, float const Z, float const t, float const T, float const dt, float const intra_sv, int const a_len, float *out)
    {
        float start_delay, start_point, drift_rate, rand, prob_up, position, step_size, time;
        int idx = blockIdx.x*blockDim.x + threadIdx.x;
        int x_pos = 0;

        curandState local_state = global_state[idx];

        start_delay = curand_uniform(&local_state)*T + (t-T/2);
        start_point = curand_uniform(&local_state)*Z + (z-Z/2);
        drift_rate = curand_normal(&local_state)*V + v;

        prob_up = .5f*(1+sqrtf(dt)/intra_sv*drift_rate);
        step_size = sqrtf(dt)*intra_sv;
        time = 0;
        position = start_point;

        while (fabs(position) > a[x_pos] & x_pos < a_len) {
            rand = curand_uniform(&local_state);
            position += ((rand < prob_up)*2 - 1) * step_size;
            time += dt;
            x_pos++;
        }

        time += start_delay;

        global_state[idx] = local_state;

        if (position <= 0) {
            out[idx] = -time;
        }
        else {
            out[idx] = time;
        }
    }

    }
    """

mod = SourceModule(code, keep=False, no_extern_c=True)

size=512
seed=1234

sim_drift = mod.get_function("sim_drift")
sim_drift_var_thresh = mod.get_function("sim_drift_var_thresh")
setup_kernel = mod.get_function("setup_kernel")

g = pycuda.curandom.XORWOWRandomNumberGenerator()
#array = pycuda.gpuarray.GPUArray((200, 400), dtype=np.float32)
#g.fill_normal(array)

#rng_states = cuda.mem_alloc(size*pycuda.characterize.sizeof('curandStateXORWOW', '#include <curand_kernel.h>'))
#setup_kernel(np.int32(size), rng_states, np.uint64(seed), np.uint64(0), block=(64,1,1), grid=(size//64+1,1))

dt = 1e-4
max_time = 5.
steps = max_time/dt
a = 2
thresh = np.array(a*np.exp(-np.linspace(0, max_time, steps)), dtype=np.float32)
thresh_gpu = gpuarray.to_gpu(thresh)

out = gpuarray.empty(size, dtype=np.float32)

def sim_drift_gpu(out, v, V, a, z, Z, t, T, size, dt=1e-4):
    sim_drift(g.state, np.float32(v), np.float32(V), np.float32(a), np.float32(z), np.float32(Z), np.float32(t), np.float32(T), np.float32(dt), np.float32(1), out, block=(64,1,1), grid=(size//64+1,1))

def sim_drift_var_thresh_gpu(out, v, V, a, z, Z, t, T, size, dt=1e-4):
    sim_drift_var_thresh(g.state, np.float32(v), np.float32(V), thresh_gpu, np.float32(z), np.float32(Z), np.float32(t), np.float32(T), np.float32(dt), np.float32(1), np.float32(max_time), out, block=(64,1,1), grid=(size//64+1,1))

sim_drift_var_thresh_gpu(out, 1, .1, thresh_gpu, 0., .1, .3, .1, size)
print out.get()

sim_drift_gpu(out, 1, .1, 2, .5, .1, .3, .1, size)
print "Out:"
print out.get()

sim_drift_gpu(out, 1, .1, 2, .5, .1, .3, .1, size)

print "Out:"
print out.get()

#rng_states.free()