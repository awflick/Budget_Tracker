# Budget Tracker
# Adam Flick
# January 2025

#to add - view all transactions and save user session so users don't have keep re-entering budget info after they close the program
import json
import os
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog


# Function to save data to a JSON file
def save_data(budget_data, budget_goals, filename="budget_data.json"):
    """
    Save the user's session data to a JSON file.

    Args:
    - budget_data: The DataFrame containing transaction data.
    - budget_goals: The dictionary containing budget goals.
    - filename: The name of the file to save the data.
    """
    # Convert DataFrame to a dictionary for JSON serialization
    data = {
        "budget_data": budget_data.to_dict(orient="records"),
        "budget_goals": budget_goals
    }
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {filename}.")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

        

# Function to save budget data to CSV
def save_to_csv(df, file_path):
    """
    Saves budget data to a CSV file.

    Args:
    - df: The DataFrame containing budget transactions.
    - file_path: The file path to save the CSV.
    """
    try:
        df.to_csv(file_path, index=False)
        print(f"Data successfully exported to CSV at {file_path}.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        
        

# Function to load data from a file (both JSON and CSV)
def load_data(json_filename="budget_data.json", csv_filename="budget_data.csv"):
    """
    Load the user's session data from both a JSON and a CSV file.

    Args:
    - json_filename: The name of the file to load the session data from (JSON).
    - csv_filename: The name of the file to load the transaction data from (CSV).

    Returns:
    - budget_tracker: A DataFrame containing transaction data.
    - budget_goals: A dictionary containing budget goals.
    """
    try:
        # Load the JSON data (budget goals and general session info)
        with open(json_filename, "r") as file:
            data = json.load(file)
            budget_goals = data.get("budget_goals", {})
            print(f"Data loaded from {json_filename}.")

        # Load the CSV data (transaction data)
        if os.path.exists(csv_filename):
            budget_tracker = pd.read_csv(csv_filename)
            print(f"CSV data loaded from {csv_filename}.")
        else:
            budget_tracker = pd.DataFrame(columns=["Date", "Type", "Category", "Amount"])
            print(f"No CSV file found, starting with empty data.")

        return budget_tracker, budget_goals

    except FileNotFoundError:
        print(f"No saved data found. Starting with empty session.")
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount"]), {}
    except json.JSONDecodeError:
        print("Error reading saved JSON data. Starting with empty session.")
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount"]), {}



# Function to get the directory for storage
def get_storage_directory():
    # For local testing, use the "user files" folder
    # For web apps or mobile apps, adapt the logic here later
    current_directory = os.getcwd()
    user_files_directory = os.path.join(current_directory, 'user files')

    # Ensure the "user files" directory exists, create it if not
    if not os.path.exists(user_files_directory):
        os.makedirs(user_files_directory)

    return user_files_directory


# Function to prompt user to select folder for saving the report
def select_save_location():
    # Set up tkinter root window (it won’t show up because we don’t call .mainloop())
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    # Ask user to choose a folder
    folder_selected = filedialog.askdirectory(title="Select Folder to Save Report")

    # If a folder is selected, return the path, else return None
    if folder_selected:
        return folder_selected
    else:
        print("No folder selected. Report will not be saved.")
        return None
    

# Validate date
def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%m-%d-%Y')
        return True
    except ValueError:
        print("Invalid date format. Please use MM-DD-YYYY.")
        return False


# Add or edit transactions
def add_edit_transactions(data, action):
    """
    Add or edit transactions in the budget tracker.

    Args:
    - data: A DataFrame containing transaction data.
    - action: 'add' for adding a new transaction, 'edit' for modifying an existing one.

    Returns:
    - Updated DataFrame with the new or modified transaction.
    """
    if action == 'add':
        # Collect and validate inputs for a new transaction
        date = input("Enter the date (MM-DD-YYYY): ")
        if not validate_date(date):
            print("Invalid date format. Transaction not added.")
            return data

        type_ = input("Enter the type (Income/Expense): ").capitalize()
        if type_ not in ['Income', 'Expense']:
            print("Invalid type. Transaction not added.")
            return data

        category = input("Enter the category (e.g., Food, Rent, Savings): ")
        try:
            amount = float(input("Enter the amount (no special characters): "))
            if amount < 0:
                print("Amount must be non-negative. Transaction not added.")
                return data
        except ValueError:
            print("Invalid amount. Transaction not added.")
            return data

        # Add the transaction safely
        new_row = {'Date': date, 'Type': type_, 'Category': category, 'Amount': amount}
        if data.empty:
            data = pd.DataFrame([new_row])
        else:
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

        print("Transaction added successfully!")

    elif action == 'edit':
        # List current transactions for selection
        if data.empty:
            print("No transactions available to edit.")
            return data

        print("\n--- Current Transactions ---")
        for index, row in data.iterrows():
            print(f"{index + 1}. Date: {row['Date']}, Type: {row['Type']}, Category: {row['Category']}, Amount: ${row['Amount']:.2f}")

        # Ask user to select a transaction to edit or delete
        try:
            transaction_num = int(input("\nEnter the number of the transaction you want to edit (0 to cancel, -1 to delete): "))
            if transaction_num == 0:
                print("Edit cancelled.")
                return data
            if transaction_num == -1:
                # Delete transaction
                delete_num = int(input("Enter the number of the transaction you want to delete: "))
                if delete_num < 1 or delete_num > len(data):
                    print("Invalid transaction number to delete.")
                    return data
                else:
                    data = data.drop(delete_num - 1).reset_index(drop=True)
                    print("Transaction deleted successfully.")
                    return data
            if transaction_num < 1 or transaction_num > len(data):
                print("Invalid transaction number.")
                return data
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return data

        # Get the row of the selected transaction
        selected_transaction = data.iloc[transaction_num - 1]

        # Display current details
        print(f"\nEditing transaction: {selected_transaction['Date']} - {selected_transaction['Type']} - {selected_transaction['Category']} - ${selected_transaction['Amount']:.2f}")

        # Get new values for the transaction
        date = input(f"Enter new date (current: {selected_transaction['Date']}): ")
        if not validate_date(date):
            print("Invalid date format. Transaction not updated.")
            return data

        type_ = input(f"Enter new type (current: {selected_transaction['Type']}): ").capitalize()
        if type_ not in ['Income', 'Expense']:
            print("Invalid type. Transaction not updated.")
            return data

        category = input(f"Enter new category (current: {selected_transaction['Category']}): ")
        try:
            amount = float(input(f"Enter new amount (current: ${selected_transaction['Amount']:.2f}): "))
            if amount < 0:
                print("Amount must be non-negative. Transaction not updated.")
                return data
        except ValueError:
            print("Invalid amount. Transaction not updated.")
            return data

        # Update the selected transaction
        data.at[transaction_num - 1, 'Date'] = date
        data.at[transaction_num - 1, 'Type'] = type_
        data.at[transaction_num - 1, 'Category'] = category
        data.at[transaction_num - 1, 'Amount'] = amount

        print("Transaction updated successfully!")

    else:
        print("Invalid action. Please choose 'add' or 'edit'.")

    return data


# add and edit budget goals
def add_edit_goals(budget_goals, action):
    """
    Adds or edits budget goals in a similar style to add_edit_transactions.
    
    Args:
    - budget_goals: A dictionary where keys are category names, and values are goal amounts.
    - action: 'add' for adding a new goal, 'edit' for modifying or deleting an existing goal.

    Returns:
    - Updated dictionary of budget goals.
    """
    if action == 'add':
        # Prompt user to add a new goal
        category = input("Enter the category name for the new goal: ").strip().title()
        try:
            goal_amount = float(input(f"Enter the budget goal amount for {category}: "))
            if goal_amount < 0:
                print("Goal amount must be non-negative. Goal not added.")
                return budget_goals
        except ValueError:
            print("Invalid input. Goal not added.")
            return budget_goals
        
        # Add the new goal
        budget_goals[category] = goal_amount
        print(f"Budget goal for '{category}' set to ${goal_amount:.2f}!")

    elif action == 'edit':
        # List current goals for selection
        if not budget_goals:
            print("No budget goals available to edit.")
            return budget_goals

        print("\n--- Current Budget Goals ---")
        goals_list = list(budget_goals.items())  # Convert dict to list of (category, amount) tuples
        for index, (cat, amt) in enumerate(goals_list, start=1):
            print(f"{index}. Category: {cat}, Goal: ${amt:.2f}")

        # Ask user to select a goal to edit or delete
        try:
            goal_num = int(input("\nEnter the number of the goal you want to edit "
                                 "(0 to cancel, -1 to delete): "))
            if goal_num == 0:
                print("Edit cancelled.")
                return budget_goals
            if goal_num == -1:
                delete_num = int(input("Enter the number of the goal you want to delete: "))
                if delete_num < 1 or delete_num > len(goals_list):
                    print("Invalid goal number to delete.")
                    return budget_goals
                else:
                    cat_to_delete = goals_list[delete_num - 1][0]
                    budget_goals.pop(cat_to_delete)
                    print(f"Goal for '{cat_to_delete}' deleted successfully.")
                    return budget_goals
            if goal_num < 1 or goal_num > len(goals_list):
                print("Invalid goal number.")
                return budget_goals
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return budget_goals

        # Proceed with editing
        selected_category, selected_amount = goals_list[goal_num - 1]

        print(f"\nEditing Goal: Category: {selected_category}, Current Goal: ${selected_amount:.2f}")

        # Prompt user for new category name (optional rename)
        new_category = input(f"Enter new category name (current: {selected_category}, press Enter to keep): ").strip().title()
        if not new_category:
            new_category = selected_category  # Keep the old name

        # Prompt user for new goal amount
        try:
            new_goal_str = input(f"Enter new goal amount (current: ${selected_amount:.2f}, press Enter to keep): ").strip()
            if new_goal_str:
                new_goal_amount = float(new_goal_str)
                if new_goal_amount < 0:
                    print("Goal amount must be non-negative. Changes not saved.")
                    return budget_goals
            else:
                new_goal_amount = selected_amount
        except ValueError:
            print("Invalid amount. Changes not saved.")
            return budget_goals

        # Update dictionary:
        # 1. Remove the old category key if the user renamed it.
        # 2. Insert the new category key or update the same key with the new amount.
        if new_category != selected_category:
            # Remove old entry
            budget_goals.pop(selected_category)
        
        # Set the new or updated goal
        budget_goals[new_category] = new_goal_amount
        print(f"Goal updated! Category: {new_category}, Amount: ${new_goal_amount:.2f}")

    else:
        print("Invalid action. Please choose 'add' or 'edit'.")

    return budget_goals



def track_budget_goals(data, goals, report=None):
    """
    Tracks actual spending/earning against budget goals.

    Args:
    - data: A DataFrame containing transaction data.
    - goals: A dictionary of budget goals by category.
    - report: The list to append the goal tracking data (default is None).

    Returns:
    - report: Updated report with goal tracking data.
    """
    if report is None:
        report = []  # Initialize report if not provided

    report.append("\n--- Budget Goals Report ---")

    if not goals:
        report.append("No goals set. Use 'set_budget_goals()' to add some!")
        return report

    actuals = data.groupby('Category')['Amount'].sum()
    for category, goal in goals.items():
        actual = actuals.get(category, 0)
        if actual > goal:
            report.append(f"⚠️ Over budget in {category}: Spent ${actual:.2f}, Goal was ${goal:.2f}")
        else:
            remaining = goal - actual
            report.append(f"✅ On track in {category}: Spent ${actual:.2f}, Remaining budget: ${remaining:.2f}")

    return report



# view budget goals
def view_budget_goals(budget_goals):
    """View the current budget goals."""
    if not budget_goals:
        print("No budget goals have been set yet.")
    else:
        print("\n--- Current Budget Goals ---")
        for category, amount in budget_goals.items():
            print(f"Category: {category}, Goal: ${amount:.2f}")
    print("\n")
    


# Generate a report
def generate_report(data, goals):
    """
    Generates a summary report of income, expenses, and trends, and tracks goals.

    Args:
    - data: A DataFrame containing transaction data.
    - goals: A dictionary of budget goals by category.

    Returns:
    - None (prints the summary report and optionally saves to a file).
    """
    if data.empty:
        print("No data available to generate a report.")
        return

    report = []

    # Total Income and Expenses
    total_income = data[data['Type'] == 'Income']['Amount'].sum()
    total_expenses = data[data['Type'] == 'Expense']['Amount'].sum()
    net_balance = total_income - total_expenses

    report.append(f"Total Income: ${total_income:.2f}")
    report.append(f"Total Expenses: ${total_expenses:.2f}")
    report.append(f"Net Balance: ${net_balance:.2f}")

    # Top Spending Categories
    expense_data = data[data['Type'] == 'Expense']
    if not expense_data.empty:
        category_totals = expense_data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        report.append("\nTop Spending Categories:")
        for category, amount in category_totals.items():
            report.append(f"  {category}: ${amount:.2f}")
    else:
        report.append("\nNo expenses recorded.")

    # Track Budget Goals
    if goals:
        report.append("\n--- Budget Goals Report ---")
        actuals = data[data['Type'] == 'Expense'].groupby('Category')['Amount'].sum()
        for category, goal in goals.items():
            actual = actuals.get(category, 0)  # Default to 0 if no spending in the category
            if actual > goal:
                report.append(f"⚠️ Over budget in {category}: Spent ${actual:.2f}, Goal was ${goal:.2f}")
            else:
                remaining = goal - actual
                report.append(f"✅ On track in {category}: Spent ${actual:.2f}, Remaining budget: ${remaining:.2f}")
    else:
        report.append("\nNo budget goals set. Use 'Set Budget Goals' to create some.")

    # Category breakdown
    report.append("\n--- Category Breakdown ---")
    category_breakdown = data.groupby('Category')['Amount'].sum()
    for category, amount in category_breakdown.items():
        report.append(f"{category}: ${amount:.2f}")

    # Monthly trends
    report.append("\n--- Monthly Trends ---")
    data['Month'] = pd.to_datetime(data['Date']).dt.to_period('M')
    monthly_trends = data.groupby(['Month', 'Type'])['Amount'].sum().unstack(fill_value=0)
    report.append(str(monthly_trends))

    # Drop the temporary 'Month' column
    data.drop(columns='Month', inplace=True, errors='ignore')

    # Print report
    for line in report:
        print(line)

    # Prompt the user to save the report
    save_report = input("\nDo you want to save this report to a file? (y/n): ").strip().lower()
    if save_report == 'y':
        export_report(report)



# export report to a file
def export_report(report):
    """
    Saves the generated report to a user-selected file location.

    Args:
    - report: The report data to be saved.
    
    Returns:
    - None
    """
    # Initialize tkinter window (used for file dialog)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open a file dialog to choose a location to save the report
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    
    if file_path:
        with open(file_path, 'w') as file:
            for line in report:
                file.write(line + '\n')
        print(f"Report saved to {file_path}")
    else:
        print("Report not saved.")
       




# Main Menu
def main_menu():
    print("\n--- Budget Tracker Main Menu ---")
    print("1. Import Budget Data from CSV")
    print("2. Load Previous Session")
    print("3. Add a Transaction")
    print("4. Edit a Transaction")
    print("5. View All Transactions")
    print("6. View Budget Summary")
    print("7. Manage Budget Goals")  # Renamed for clarity
    print("8. View Budget Goals") 
    print("9. Generate Report")
    print("10. Save Program Data")
    print("11. Export to CSV File")
    print("12. Exit")
    return input("Choose an option (1-12): ")



# Main Program
def budget_tracker():
    # Get the directory for storage
    storage_directory = get_storage_directory()
    
    # Define file paths for JSON and CSV
    json_file_path = os.path.join(storage_directory, 'budget_data.json')  # For JSON persistence
    csv_file_path = os.path.join(storage_directory, 'budget_data.csv')  # For CSV export

    # Set default state (blank) upon startup
    budget_data = pd.DataFrame(columns=["Date", "Type", "Category", "Amount"])  # Blank DataFrame for transactions
    budget_goals = {}  # Empty dictionary for budget goals
    
    while True:
        choice = main_menu()

        if choice == '1':  # Import Budget Data
            try:
                file_path = input("Enter the path to your CSV file: ")
                budget_data = pd.read_csv(file_path)
                print("Data successfully imported!")

                # Validate and clean column names
                expected_columns = ['Date', 'Type', 'Category', 'Amount']
                renamed_columns = {
                    'date': 'Date',
                    'type': 'Type',
                    'category': 'Category',
                    'amount': 'Amount'
                }

                # Rename columns to standard names (case-insensitive)
                budget_data.rename(columns=lambda x: renamed_columns.get(x.lower(), x), inplace=True)

                # Drop rows where all columns are NaN (e.g., blank rows)
                budget_data.dropna(how='all', inplace=True)

                # Check if all required columns are present
                missing_columns = [col for col in expected_columns if col not in budget_data.columns]
                if missing_columns:
                    print(f"Error: Missing required columns in the CSV file: {missing_columns}")
                    print("Please ensure your CSV has the following columns: Date, Type, Category, Amount.")
                    budget_data = pd.DataFrame()  # Reset budget_data to an empty DataFrame
                else:
                    print("CSV structure is valid.")
                    print(budget_data.head())

                    # Drop rows with invalid or missing values in required columns
                    budget_data.dropna(subset=['Date', 'Type', 'Category', 'Amount'], inplace=True)

                    # Validate data in the 'Type' column
                    valid_types = ['Income', 'Expense']
                    if not all(budget_data['Type'].isin(valid_types)):
                        print("Warning: Some transactions in the 'Type' column are invalid or missing.")
                        print(f"Valid 'Type' values should be: {valid_types}")
                        print("Please review and correct your CSV file if needed.")

            except Exception as e:
                print(f"Error importing data: {e}")

        elif choice == '2':  # Load Previous Session
            budget_data, budget_goals = load_data(json_filename=json_file_path, csv_filename=csv_file_path)  # Load the saved session
            print("Previous session loaded.")

        elif choice == '3':  # Add a Transaction
            budget_data = add_edit_transactions(budget_data, 'add')

        elif choice == '4':  # Edit a Transaction
            budget_data = add_edit_transactions(budget_data, 'edit')

        elif choice == '5':  # View All Transactions
            print("\n--- Current Transactions ---")
            if budget_data.empty:
                print("No transactions to display.")
            else:
                for index, row in budget_data.iterrows():
                    print(f"{index + 1}. Date: {row['Date']}, Type: {row['Type']}, Category: {row['Category']}, Amount: ${row['Amount']:.2f}")

        elif choice == '6':  # View Summary
            if budget_data.empty:
                print("No data loaded. Please import a CSV first.")
            else:
                total_income = budget_data[budget_data['Type'] == 'Income']['Amount'].sum()
                total_expenses = budget_data[budget_data['Type'] == 'Expense']['Amount'].sum()
                balance = total_income - total_expenses
                print(f"\n--- Totals Summary ---")
                print(f"Total Income: ${total_income:.2f}")
                print(f"Total Expenses: ${total_expenses:.2f}")
                print(f"Balance: ${balance:.2f}")

        elif choice == '7':  # Manage Budget Goals
            if not budget_goals:
                print("No budget goals set yet.")
    
            sub_choice = input("Would you like to (A)dd or (E)dit existing goals? (a/e): ").strip().lower()
            if sub_choice == 'a':
                budget_goals = add_edit_goals(budget_goals, 'add')
            elif sub_choice == 'e':
                budget_goals = add_edit_goals(budget_goals, 'edit')
            else:
                print("Invalid choice. No changes made to goals.")

        elif choice == '8':  # View Budget Goals
            if budget_goals:
                print("\n--- Current Budget Goals ---")
                view_budget_goals(budget_goals)
            else:
                print("\nNo budget goals set. Use 'Set Budget Goals' to add some!")

        elif choice == '9':  # Generate Report
            if budget_data.empty:
                print("No data loaded. Please import a CSV first.")
            else:
                generate_report(budget_data, budget_goals)

        elif choice == '10':  # Save Program Data to JSON
            if budget_data.empty and not budget_goals:
                print("No data or goals to save. Nothing to save.")
            else:
                save_data(budget_data, budget_goals, json_file_path)  # Save session data to JSON

        elif choice == '11':  # Export Data to CSV
            if budget_data.empty:
                print("No transactions available to export. Nothing to save.")
            else:
                csv_file_path = os.path.join(storage_directory, 'budget_data.csv')  # Define CSV file path
                save_to_csv(budget_data, csv_file_path)  # Save to CSV

        elif choice == '12':  # Exit
            print("Exiting the program. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 12.")



# Run program
if __name__ == "__main__":
    budget_tracker()


