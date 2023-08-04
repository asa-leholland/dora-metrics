from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Create dataframe
data = {
    "Date": ["3/29/23", "4/5/23", "4/12/23", "5/17/23", "7/5/23", "7/5/23", "6/21/23",
             "6/7/23", "4/12/23", "4/26/23", "5/3/23", "5/10/23", "6/14/23", "6/7/23",
             "5/31/23", "7/12/23", "7/12/23", "7/12/23", "8/2/23", "5/10/23", "5/17/23",
             "7/5/23", "7/5/23", "6/7/23", "8/2/23", "8/2/23", "8/2/23", "6/14/23", "6/7/23"],
    "App Name": ["Admin", "Admin", "Admin", "Admin", "Admin", "Admin", "Admin",
                 "BOM API", "FPKG", "FPKG", "FPKG", "FPKG", "FPKG", "FPKG",
                 "FPKG", "IMS API", "IMS API", "IMS API", "IMS API", "SFS Testcard",
                 "SFS Testcard", "SFS Testcard", "SFS Testcard", "SFS Testcard",
                 "SFS Testcard", "SFSD API", "SFSD UI", "TPS", "TPS"],
    "Average Lead Time": [2, 2, 4, 11, 2, 2, 5.5, 6, 1, 13, 5, 1, 3, 9, 31, 32, 32,
                          32, 20, 135, 6, 25, 25, 7, 38, 15, 2, 3, 18]
}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

# Group by 'App Name' and 'Date', then calculate the average 'Average Lead Time' for each group
df_grouped = df.groupby(['App Name', 'Date'])['Average Lead Time'].mean().reset_index()

# Plotting
plt.figure(figsize=(12,8))
colors = plt.cm.viridis(np.linspace(0, 1, df_grouped['App Name'].nunique()))

for i, app_name in enumerate(df_grouped['App Name'].unique()):
    app_data = df_grouped[df_grouped['App Name'] == app_name]
    app_data = app_data.sort_values('Date')

    # Plot points
    plt.scatter(app_data['Date'], app_data['Average Lead Time'], color=colors[i], label=app_name)

    # Plot smoothed line
    xnew = np.linspace(app_data['Date'].min().value, app_data['Date'].max().value, 300)

    if len(app_data['Date']) > 2:  # Create a cubic spline if there are more than 2 data points
        spl = make_interp_spline(app_data['Date'].apply(lambda x: x.value), app_data['Average Lead Time'], k=3)  # BSpline object
        y_smooth = spl(xnew)
        plt.plot(pd.to_datetime(xnew), y_smooth, color=colors[i])
    elif len(app_data['Date']) > 1:  # Create a linear spline if there are more than 1 data points
        spl = make_interp_spline(app_data['Date'].apply(lambda x: x.value), app_data['Average Lead Time'], k=1)  # BSpline object
        y_smooth = spl(xnew)
        plt.plot(pd.to_datetime(xnew), y_smooth, color=colors[i])

plt.xlabel("Date")
plt.ylabel("Average Lead Time (Days)")
plt.title("Average Lead Time by App Name")
plt.legend(title="App Name")
plt.grid(True)
plt.show()