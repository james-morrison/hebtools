gravity = 9.81
density_seawater = 1025

import math

def get_wavelength(peak_period, depth):
    """
        Takes the peak period and calculates
        the wavelength for any depth in metres
    """
    energy_period = 0.9 * peak_period
    numerator= gravity * ( energy_period**2 )
    denominator= 2 * math.pi
    first_result = numerator / denominator
    estimated_wavelength = first_result

    def tan_h_func(depth, estimated_wavelength):
        return math.tanh( ( ( 2 * math.pi ) * depth ) / estimated_wavelength )
    
    tan_h = tan_h_func(depth, estimated_wavelength)
    L = tan_h * first_result
    diff= L - estimated_wavelength
    while diff > 0.01 or diff < -0.01:
        tan_h = tan_h_func(depth, estimated_wavelength)
        L = tan_h * first_result
        diff = L - estimated_wavelength
        estimated_wavelength = estimated_wavelength + ( 0.5 * diff )
    return estimated_wavelength
    
def calculate(sig_wave_height, peak_period, depth):
    """ Given significant wave height in metres and peak period Tp in seconds
        a tuple with wave power in kW per metre wave crest and wavelength in
        metres is returned.
    """

    def calculate_wave_power(sig_wave_height, group_velocity):
        return gravity * density_seawater * ( (sig_wave_height ** 2) /16 ) * \
               group_velocity

    def calculate_wave_number(wavelength):
        return (2 * math.pi)/wavelength
        
    def get_celerity(wavelength, peak_period, depth):
        energy_period = 0.9 * peak_period
        gT_over_two_pi = ( gravity * energy_period ) / ( 2 * math.pi )
        tan_h = math.tanh( ( ( 2 * math.pi ) * depth) / wavelength)
        return gT_over_two_pi * tan_h
        
    def calculate_group_velocity(wavelength, peak_period, depth):
        celerity = get_celerity(wavelength, peak_period, depth)
        wave_number = calculate_wave_number(wavelength)
        numerator= 2 * wave_number * depth
        denominator = math.sinh(numerator)
        result = 1 + (numerator / denominator)
        return 0.5 * result * celerity
        
    def get_wave_power_in_kw_p_m(sig_wave_height, peak_period, depth):
        wavelength = get_wavelength(peak_period, depth)
        group_velocity = calculate_group_velocity(wavelength, peak_period, 
                                                  depth)
        wave_power = float(calculate_wave_power(sig_wave_height, 
                                                group_velocity))/1000
        return wave_power
        
    return get_wave_power_in_kw_p_m(sig_wave_height, peak_period, depth)
