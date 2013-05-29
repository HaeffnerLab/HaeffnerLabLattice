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

    def ion_model(self, params, xx, yy, include_ions = True):
        '''
        model for fitting ions on the CCD image
        xx and yy are the provided meshgrid of the coordinate system and zz are the values
        include_ions is True to include all the ions. can also be an ion-long array of booleans of which ions to include
        '''
        ion_number = int(params['ion_number'].value)
        if include_ions is True:
            include_ions = [True] * ion_number
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
            fit += self.ion_gaussian(xx_rotated, yy_rotated, x_center, y_center, sigma, sigma, amplitude) * include_ions[i]
        return fit

    def ion_chain_fit(self, params , xx, yy,  data, include_ions = True):
        model = self.ion_model(params, xx, yy, include_ions)
        scaled_difference = (model - data) / np.sqrt(data)
        return scaled_difference.ravel()

    def guess_parameters_and_fit(self, xx, yy, data, ion_number):
        params = lmfit.Parameters()
        params.add('ion_number', value = ion_number, vary = False)
        background_guess = np.average(data) #assumes that the data is mostly background apart from few peaks
        background_std = np.std(data)
        center_x_guess,center_y_guess,amplitude_guess = self.guess_centers(data, background_guess, background_std, xx, yy)
        sigma_guess = 1#assume it's hard to resolve the ion, sigma ~ 1
        spacing_guess = 10 * sigma_guess #assumes ions are separate
        params.add('background_level', value = background_guess, min = 0.0)
        params.add('amplitude', value = amplitude_guess, min = 0.0)
        params.add('rotation_angle', value = 0.0, min = -np.pi, max = np.pi, vary = False)
        params.add('center_x', value = center_x_guess, min = 0, max = 657)
        params.add('center_y', value = center_y_guess, min = 0, max = 495)
        params.add('spacing', value = spacing_guess, min = 2.0, max = 495)
        params.add('sigma', value = sigma_guess, min = 0.0, max = 10.0)
        #first fit without the angle
        lmfit.minimize(self.ion_chain_fit, params, args = (xx, yy, data))
        #allow angle to vary and then fit again
        params['rotation_angle'].vary = True
        result = lmfit.minimize(self.ion_chain_fit, params, args = (xx, yy, data))
        return result, params
    
    def guess_centers(self, data, background, background_std, xx, yy):
        '''
        guesses the center of the ion from the data
        
        starts with a threshold of 3 standard deviations above the background and gets 
        the average positions of all pixels higher than this value
        
        if none are found, lowers the threshold
        '''
        thresholds = np.arange(3,0,-1)
        for threshold in thresholds:
            #print threshold
            amplitude_guess = background + threshold * background_std
            where_peak = np.where(data > amplitude_guess)
            peaks_y, peaks_x = yy[where_peak], xx[where_peak]
            if peaks_x.size and peaks_y.size:
                center_y_guess= peaks_y.mean()
                center_x_guess = peaks_x.mean()
                amplitude_guess = threshold * background_std
                return center_x_guess, center_y_guess, amplitude_guess
        raise Exception("Unable to guess ion center from the data")
    
    def state_detection(self, xx, yy, image, reference_image_params):
        '''
        given the image and the parameters of the reference images with all ions bright, determines
        which ions are currently darks
        '''
        ion_number = reference_image_params['ion_number'].value
        bright_ions = np.empty(ion_number)
        differences = np.empty(ion_number)
        #evaluate chi squred for an all-dark state
        dark_state = np.zeros(ion_number)
        chi_dark = ((self.ion_chain_fit(reference_image_params, xx, yy, image, dark_state))**2).sum()
        for current_ion in range(ion_number):
            #cycling over each ion comparing chi squred with each one bright with the all-dark state
            bright_state = np.zeros(ion_number)
            bright_state[current_ion] = 1
            chi_bright = ((self.ion_chain_fit(reference_image_params, xx, yy, image, bright_state))**2).sum()
#             print bright_state, chi_bright, chi_dark, chi_bright <= chi_dark
            #current ion is bright if bright chi squared is less than dark
            bright_ions[current_ion] = chi_bright <= chi_dark
            differences[current_ion] = (chi_bright - chi_dark) / chi_dark
        return bright_ions, differences
        
    def report(self, params):
        lmfit.report_errors(params)
    
    def graph(self, x_axis, y_axis, image, params, result):
        #plot the sample data
        from matplotlib import pyplot
        pyplot.contourf(x_axis, y_axis, image, alpha = 0.5)
        #plot the fit
        #sample the fit with more precision
        x_axis_fit = np.linspace(x_axis.min(), x_axis.max(), x_axis.size * 5)
        y_axis_fit = np.linspace(y_axis.min(), y_axis.max(), y_axis.size * 5)
        xx, yy = np.meshgrid(x_axis_fit, y_axis_fit)
        fit = self.ion_model(params, xx, yy)
        pyplot.contour(x_axis_fit, y_axis_fit, fit, colors = 'k', alpha = 0.75)
        pyplot.annotate('chi sqr {}'.format(result.redchi), (0.5,0.8), xycoords = 'axes fraction')
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
    sample_params.add('spacing', value = 12.0)
    sample_params.add('sigma', value = 1.0)
    fitter = linear_chain_fitter()
    sample_data = fitter.ion_model(sample_params, xx, yy)
    #plot the sample data
    from matplotlib import pyplot
    pyplot.contourf(x_axis, y_axis, sample_data, alpha = 0.1)
    #perform the fit with some some guessed starting parameters
    result, params = fitter.guess_parameters_and_fit(xx, yy, sample_data, ion_number = 5)
    print result.nfev, result.success, result.redchi
    fitter.report(params)
    #plot the fit
    fitter.graph(x_axis, y_axis, sample_data, params, result)
    pyplot.show()