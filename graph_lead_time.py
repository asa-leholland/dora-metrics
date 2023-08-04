import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Load the data
df = pd.read_csv('Book1.csv')

# Parse dates
df['Date'] = pd.to_datetime(df['Date'])

# Filter out zero or null values in 'Average Lead Time'
df = df[df['Average Lead Time'].notnull() & (df['Average Lead Time'] != 0)]

# Get unique App Names
app_names = df['App Name'].unique()

# Create a plot for each App Name
for app in app_names:
    app_data = df[df['App Name'] == app]
    plt.scatter(app_data['Date'], app_data['Average Lead Time'], label=app)
    plt.plot(app_data['Date'], app_data['Average Lead Time'], linestyle='dotted', color=plt.gca().lines[-1].get_color())

plt.xlabel('Date')
plt.ylabel('Average Lead Time (days)')
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))  # limit number of x-axis labels
plt.legend()
plt.show()
