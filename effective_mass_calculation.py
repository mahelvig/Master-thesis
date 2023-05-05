# Program to calculate effective mass

mass_oxygen = 16
mass_hydrogen = 1
mass_no = 14+16
mass_o2 = 16*2

density_o = 70
density_h = 100 -density_o
density_no= 0
density_o2= 0

mass    = {'hydrogen' :mass_oxygen,
           'oxygen'   :mass_hydrogen,
           'no':  mass_no,
           'o2':  mass_o2,
}

density = {'hydrogen':density_o,
            'oxygen':density_h,
            'no':  density_no,
            'o2':  density_o2,
            }

density_tot =  sum(density.values())


m_eff_under = 0
summen = 0
for key in mass:
  summen += density[key]/mass[key]

m_eff_under = 1/density_tot * summen

print(f'Effective mass: {1/m_eff_under:.1f}')
print(f'Percentage of H: {density_h*100/density_tot:.1f}')
print(f'Percentage of NO: {density_no*100/density_tot:.1f}')
print(f'Percentage of O2: {density_o2*100/density_tot:.1f}')
