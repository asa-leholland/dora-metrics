import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Read the Excel data into a DataFrame
df = pd.read_excel('Book1.xlsx')

# Clean the column names by removing any invisible characters
df.columns = df.columns.str.replace('\u200b', '')

# Print the column names to verify their correctness
print(df.columns)

# Update the column names in the numeric_columns list
numeric_columns = ['Deployment Count', 'Median Time to Restore Service', 'Average Lead Time', 'Change Failure Rate']

# Convert the relevant columns to numeric types
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Sort the DataFrame by the 'Date' column
df = df.sort_values('Date')

# Drop duplicate rows based on date and app name
df = df.drop_duplicates(subset=['Date'])

# Get the number of columns (excluding 'Date')
num_columns = len(df.columns) - 1

# Determine the number of rows and columns for the grid layout
num_rows = (num_columns + 1) // 2
num_cols = min(num_columns, 2)

# Create a PDF to save the graphs
pdf_pages = PdfPages('graphs.pdf')

# Create a figure with the determined grid layout
fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(10, 8))

# Iterate over each column (except the first) and create a graph in the corresponding subplot
plot_counter = 0  # Track the number of successful plots
for i, column in enumerate(df.columns[1:], start=1):
    if column != 'App Name' and df[column].notna().any():  # Exclude 'App Name' column and empty columns
        ax = axes[plot_counter // num_cols, plot_counter % num_cols]
        ax.set_title(column)
        ax.set_xlabel('Date')
        ax.set_ylabel(column)

        # Plot the data for the column
        ax.plot(df['Date'], df[column])

        ax.tick_params(axis='x', rotation=45)

        plot_counter += 1  # Increment plot counter for successful plots

# Adjust the layout and spacing between subplots
plt.tight_layout()

# Save the figure to the PDF page
pdf_pages.savefig(fig)
plt.close()

# Save the PDF file and close it
pdf_pages.close()
