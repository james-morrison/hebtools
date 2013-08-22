gravity = 9.81
density_seawater = 1025

import math

class Wave_Power:
    def __init__(self, sig_wave_height_cm, peak_period, depth):
        self.get_wave_power_in_kw_p_m(sig_wave_height_cm,peak_period, depth)
        
    def calculate_wave_power(self, sig_wave_height_cm, group_velocity):
        sig_wave_height_metres = float(sig_wave_height_cm)/100
        return gravity * density_seawater * \
               ( (sig_wave_height_metres ** 2) /16 ) * group_velocity

    def calculate_wavelength(self, peak_period, depth):
        """
            Takes the peak period and calculates
            the wavelength for any depth in metres
        """
        energy_period = 0.9 * peak_period
        numerator= gravity * ( energy_period**2 )
        denominator= 2 * math.pi
        first_result = numerator / denominator
        estimated_wavelength = first_result

        tan_h = math.tanh( ( ( 2 * math.pi ) * depth) / estimated_wavelength )
        L = tan_h * first_result
        diff= L - estimated_wavelength
        while diff > 0.01 or diff < -0.01:
            tan_h = math.tanh( ( (2 * math.pi) * depth)/ estimated_wavelength )
            L = tan_h * first_result
            diff = L - estimated_wavelength
            estimated_wavelength = estimated_wavelength + ( 0.5 * diff )
        return estimated_wavelength

    def calculate_wave_number(self, depth):
        return (2 * math.pi)/ self.wavelength
        
    def get_celerity(self, peak_period, depth):
        energy_period = 0.9 * peak_period
        gT_over_two_pi = ( gravity * energy_period ) / ( 2 * math.pi )
        tan_h = math.tanh( ( ( 2 * math.pi ) * depth) / self.wavelength)
        return gT_over_two_pi * tan_h
        
    def calculate_group_velocity(self, peak_period, depth):
        celerity = self.get_celerity(peak_period, depth)
        wave_number = self.calculate_wave_number(depth)
        numerator= 2 * wave_number * depth
        denominator = math.sinh(numerator)
        result = 1 + (numerator / denominator)
        return 0.5 * result * celerity
        
    def get_wave_power_in_kw_p_m(self, sig_wave_height_cm, peak_period, depth):
        self.wavelength = self.calculate_wavelength( peak_period, depth )
        group_velocity = self.calculate_group_velocity( peak_period, depth )
        self.wave_power = float(self.calculate_wave_power(sig_wave_height_cm, 
                                                          group_velocity))/1000
