from generation_debt import Generate_Yield

start_date = '2023-01-01'
end_date = '2023-04-30'

test = Generate_Yield()
test.generate_yield_spread(start_date, end_date, 'Daily', '5y', '1y')

print(test.yielddiff_lf.describe())