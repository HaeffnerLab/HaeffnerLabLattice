from __future__ import division
import numpy as np
from equilbrium_positions import position_dict
import lmfit

class linear_chain_fitter(object):

    def ion_gaussian(self, xx, yy, x_center, y_center, sigma_x, sigma_y, amplitude):
        '''
        xx and yy are the provided meshgrid of x and y coordinates
        generates a 2D gaussian for an ion centered at x_center and y_center
        '''
        result = amplitude * np.exp( - (xx - x_center)**2 / (2 * sigma_x**2)) *  np.exp( - (yy - y_center)**2 / (2 * sigma_y**2))
        return result

    def ion_model(self, params, xx, yy):
        '''
        model for fitting ions on the CCD image
        xx and yy are the provided meshgrid of the coordinate system and zz are the values
        '''
        ion_number = int(params['ion_number'].value)
        background_level = params['background_level'].value
        amplitude = params['amplitude'].value #all ions are assumsed to have the same amplitude
        rotation_angle = params['rotation_angle'].value #angle of the ion axis with respect to the xx and yy coordinate system
        ion_center_x = params['center_x'].value #center of the ions
        ion_center_y = params['center_y'].value #center of the ions
        spacing = params['spacing'].value #spacing constant of the ions
        sigma = params['sigma'].value #width along the axis
        
        #first we rotate the data by the rotation_angle
        xx_rotated = xx * np.cos(rotation_angle) - yy  * np.sin(rotation_angle)
        yy_rotated = xx * np.sin(rotation_angle) + yy  * np.cos(rotation_angle)
        
        fit = np.ones_like(xx) * background_level
        for i in range(ion_number):
            x_center = ion_center_x + spacing * position_dict[ion_number][i]
            y_center = ion_center_y
            fit += self.ion_gaussian(xx_rotated, yy_rotated, x_center, y_center, sigma, sigma, amplitude)
        return fit

    def ion_chain_fit(self, params , xx, yy,  data):
        model = self.ion_model(params, xx, yy)
        return (model - data).ravel()

    def guess_parameters_and_fit(self, xx, yy, data, ion_number):
        print xx
        params = lmfit.Parameters()
        params.add('ion_number', value = ion_number, vary = False)
        background_guess = np.average(data) #assumes that the data is mostly background apart from few peaks
        background_std = np.std(data)
        amplitude_guess = background_guess + 3 * background_std
        where_peak = np.where(data > amplitude_guess)
        peaks_y, peaks_x = yy[where_peak], xx[where_peak]
        center_y_guess= peaks_y.mean()
        center_x_guess = peaks_x.mean()
        sigma_guess = 1#assume it's hard to resolve the ion, sigma ~1
        spacing_guess = 5 * sigma_guess #assumes ions are separate
        params.add('background_level', value = background_guess, min = 0.0)
        params.add('amplitude', value = amplitude_guess, min = 0.0)
        params.add('rotation_angle', value = 0, min = 0.0, max = np.pi)
        params.add('center_x', value = center_x_guess, min = 0, max = 657)
        params.add('center_y', value = center_y_guess, min = 0, max = 495)
        params.add('spacing', value = spacing_guess, min = 0.0, max = 495)
        params.add('sigma', value = sigma_guess, min = 0.0, max = 400)
        result = lmfit.minimize(self.ion_chain_fit, params, args = (xx, yy, data))
        return result, params
    
    def report(self, params):
        lmfit.report_errors(params)
    
    def graph(self, x_axis, y_axis, image, result):
        #plot the sample data
        import matplotlib
        matplotlib.use('Qt4Agg')
        from matplotlib import pyplot
        pyplot.contourf(x_axis, y_axis, image, alpha = 0.5)
        result = image + np.reshape(result.residual, (y_axis.size, x_axis.size))
        #plot the fit
        pyplot.contour(x_axis, y_axis, result, colors = 'k')
        pyplot.show()

if __name__ == '__main__':
    #generate sample data
    x_axis = np.linspace(0, 100, 101)
    y_axis = np.linspace(0, 150, 151)
    xx, yy = np.meshgrid(x_axis, y_axis)
    sample_params = lmfit.Parameters()
    sample_params.add('ion_number', value = 5)
    sample_params.add('background_level', value = 120)
    sample_params.add('amplitude', value = 500)
    sample_params.add('rotation_angle', value = 5 * np.pi / 180.0)
    sample_params.add('center_x', value = 50.0)
    sample_params.add('center_y', value = 75.0)
    sample_params.add('spacing', value = 5.0)
    sample_params.add('sigma', value = 1.0)
    fitter = linear_chain_fitter()
    sample_data = fitter.ion_model(sample_params, xx, yy)
    #plot the sample data
    import matplotlib
    matplotlib.use('Qt4Agg')
    from matplotlib import pyplot
    pyplot.contourf(x_axis, y_axis, sample_data, alpha = 0.1)
    #perform the fit with some some guessed starting parameters
    result, params = fitter.guess_parameters_and_fit(xx, yy, sample_data, ion_number = 5)
    fitter.report(params)
    result = sample_data + np.reshape(result.residual, (y_axis.size, x_axis.size))
    #plot the fit
    pyplot.contour(x_axis, y_axis, result, 5)
    pyplot.show()