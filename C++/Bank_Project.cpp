#include <iostream>
#include <string>
#include <vector>

using namespace std;

class BankAccount{
    protected:
        string AccName;
        int AccNum;
        double Balance;
    
    public:
        // Default constructor
        BankAccount() : AccName(""), AccNum(0), Balance(0.0) {} 
        
        // Parameterized constructor
        BankAccount(string name, int number, double initial_balance){
            AccName = name;
            AccNum = number;
            Balance = initial_balance;
        }
        
        // Destructor
        ~BankAccount(){
            // Account cleanup
        }
        
        // Method to get account information from user input
        virtual void GetInfo(){
            cout << "\n--- Creating New Account ---" << endl;
            cout << "Enter account holder name: ";
            cin.ignore(); // Clear input buffer
            getline(cin, AccName);
            cout << "Enter account number: ";
            cin >> AccNum;
            cout << "Enter initial balance: $";
            cin >> Balance;
        }
        
        // Method to deposit money
        void Deposit(double amount){
            if(amount <= 0){
                cout << "\nInvalid deposit amount! Please enter a positive value." << endl;
                return;
            }
            Balance += amount;
            cout << "\nDeposit successful! $" << amount << " was deposited to your account" 
                 << "\nNew balance: $" << Balance << endl;
        }
        
        // Method to withdraw money
        void Withdraw(double amount){
            if(amount <= 0){
                cout << "\nInvalid withdrawal amount! Please enter a positive value." << endl;
                return;
            }
            if(amount > Balance){
                cout << "\nInsufficient Funds! Your current balance is $" << Balance << endl;
            } else{
                Balance -= amount;
                cout << "\nWithdrawal successful! $" << amount << " was withdrawn from your account" 
                     << "\nNew balance: $" << Balance << endl;
            }
        }
        
        // Method to display account information
        virtual void ShowInfo(){
            cout << "\n\n\n";
            cout << "\n---------------------------";
            cout << "\nAccount Holder: " << AccName;
            cout << "\nAccount Number: " << AccNum;
            cout << "\nAccount Balance: $" << Balance;
            cout << "\n---------------------------" << endl;
            cout << "\n\n\n";
        }
        
        // Getter methods - these allow access to protected variables
        string getName() const { return AccName; }
        int getAccNum() const { return AccNum; }
        double getBalance() const { return Balance; }
        
        // Setter method - allows modifying balance safely
        void setBalance(double newBalance) { Balance = newBalance; }
};

class SavingsAccount : public BankAccount{
    private:
        double interest;
    
    public:
        // Default constructor
        SavingsAccount() : BankAccount(), interest(5.5) {}
        
        // Parameterized constructor
        SavingsAccount(string name, int number, double initial_balance, double InterestRate) 
            : BankAccount(name, number, initial_balance){
            interest = InterestRate;
        }
        
        // Override GetInfo to add interest functionality
        void GetInfo() override {
            BankAccount::GetInfo(); // Call parent method first
            
            // Apply welcome bonus interest
            double interestAmount = Balance * (interest / 100);
            Balance += interestAmount;
            cout << "\nWelcome bonus interest of $" << interestAmount << " applied!" 
                 << "\nNew Balance: $" << Balance << endl;
        }
        
        // Override ShowInfo to include interest rate
        void ShowInfo() override {
            BankAccount::ShowInfo();
            cout << "Interest Rate: " << interest << "%" << endl;
        }
        
        // Method to apply interest to the account
        void applyInterest(){
            double interestAmount = Balance * (interest / 100);
            Balance += interestAmount;
            cout << "\nInterest of $" << interestAmount << " applied to account " << AccNum 
                 << "\nNew balance: $" << Balance << endl;
        }
        
        // Method to transfer money to another savings account
        void transfer(SavingsAccount& recipient){
            string recipientName;
            double amount;
            
            cout << "\n--- Transfer Money ---" << endl;
            cout << "Enter recipient account holder name: ";
            cin.ignore(); // Clear input buffer
            getline(cin, recipientName);
            
            // Check if recipient name matches
            if (recipient.AccName != recipientName) {
                cout << "\nError: Recipient account name does not match! Transfer cancelled." << endl;
                return;
            }
            
            cout << "Your current balance: $" << Balance << endl;
            cout << "How much do you want to transfer? $";
            cin >> amount;
            
            // Validate transfer amount
            if(amount <= 0){
                cout << "\nInvalid transfer amount! Please enter a positive value." << endl;
                return;
            }
            
            if (Balance < amount) {
                cout << "\nInsufficient Funds! Transfer cancelled." << endl;
            } else {
                Balance -= amount;
                recipient.Balance += amount;
                cout << "\nTransfer successful!" 
                     << "\nYour new balance: $" << Balance
                     << "\nRecipient's new balance: $" << recipient.Balance << endl;
            }
        }
        
        // Getter for interest rate
        double getInterestRate() const { return interest; }
};

// Function to find an account by account number
SavingsAccount* findAccount(vector<SavingsAccount>& accounts, int accNum){
    // Loop through all accounts to find matching account number
    for(int i = 0; i < accounts.size(); i++){
        if(accounts[i].getAccNum() == accNum){
            return &accounts[i]; // Return address of found account
        }
    }
    return nullptr; // Return null if account not found
}

// Function to display all accounts
void displayAllAccounts(const vector<SavingsAccount>& accounts){
    if(accounts.empty()){
        cout << "\nNo accounts created yet." << endl;
        return;
    }
    
    cout << "\n========== ALL ACCOUNTS ==========" << endl;
    for(int i = 0; i < accounts.size(); i++){
        cout << "\nAccount Number: " << accounts[i].getAccNum() 
             << " | Holder: " << accounts[i].getName() 
             << " | Balance: $" << accounts[i].getBalance()
             << " | Interest Rate: " << accounts[i].getInterestRate() << "%" << endl;
    }
    cout << "===================================" << endl;
}

// Simple function to clear input problems
void clearInput(){
    cin.clear(); // Reset error flags
    string dummy;
    getline(cin, dummy); // Read and discard the problematic input
}

// Function to get valid integer input
int getValidIntInput(){
    int value;
    // Keep asking until user enters a valid integer
    while(!(cin >> value)){
        cout << "\nInvalid input! Please enter a valid number: ";
        clearInput(); // Clear the bad input
    }
    return value;
}

// Function to get valid decimal input
double getValidDoubleInput(){
    double value;
    // Keep asking until user enters a valid decimal number
    while(!(cin >> value)){
        cout << "\nInvalid input! Please enter a valid amount: ";
        clearInput(); // Clear the bad input
    }
    return value;
}

int main(){
    vector<SavingsAccount> accounts; // Store all accounts here
    int choice;

    cout << "\n\n\n";
    cout << "       === Welcome to the ===" << endl;
    cout << "=== Alpha Project Banking System ===" << endl;

    // Main program loop
    do {
        // Show menu options
        cout << "\n\n\n";
        cout << "\n========== MAIN MENU ==========" << endl;
        cout << "1. Create New Account" << endl;
        cout << "2. Deposit Money" << endl;
        cout << "3. Withdraw Money" << endl;
        cout << "4. Transfer Money" << endl;
        cout << "5. Apply Interest" << endl;
        cout << "6. View Account Details" << endl;
        cout << "7. View All Accounts" << endl;
        cout << "8. Exit" << endl;
        cout << "===============================" << endl;
        cout << "Enter your choice (1-8): ";
        
        choice = getValidIntInput();
        cout << "\n\n\n";
        
        // Handle user's choice
        switch(choice){
            case 1: {
                // Create new account
                SavingsAccount newAccount;
                newAccount.GetInfo();
                accounts.push_back(newAccount); // Add account to vector
                cout << "\nAccount created successfully!" << endl;
                break;
            }
            
            case 2: {
                // Deposit money
                if(accounts.empty()){
                    cout << "\nNo accounts available. Please create an account first." << endl;
                    break;
                }
                
                cout << "\nEnter account number for deposit: ";
                int accNum = getValidIntInput();
                SavingsAccount* account = findAccount(accounts, accNum);
                
                if(account){
                    cout << "Enter deposit amount: $";
                    double amount = getValidDoubleInput();
                    account->Deposit(amount);
                } else {
                    cout << "\nAccount not found!" << endl;
                }
                break;
            }
            
            case 3: {
                // Withdraw money
                if(accounts.empty()){
                    cout << "\nNo accounts available. Please create an account first." << endl;
                    break;
                }
                
                cout << "\nEnter account number for withdrawal: ";
                int accNum = getValidIntInput();
                SavingsAccount* account = findAccount(accounts, accNum);
                
                if(account){
                    cout << "Enter withdrawal amount: $";
                    double amount = getValidDoubleInput();
                    account->Withdraw(amount);
                } else {
                    cout << "\nAccount not found!" << endl;
                }
                break;
            }
            
            case 4: {
                // Transfer money between accounts
                if(accounts.size() < 2){
                    cout << "\nAt least 2 accounts required for transfer. Current accounts: " 
                         << accounts.size() << endl;
                    break;
                }
                
                cout << "\nEnter sender's account number: ";
                int senderAccNum = getValidIntInput();
                SavingsAccount* sender = findAccount(accounts, senderAccNum);
                
                if(!sender){
                    cout << "\nSender account not found!" << endl;
                    break;
                }
                
                cout << "Enter recipient's account number: ";
                int recipientAccNum = getValidIntInput();
                SavingsAccount* recipient = findAccount(accounts, recipientAccNum);
                
                if(!recipient){
                    cout << "\nRecipient account not found!" << endl;
                    break;
                }
                
                if(senderAccNum == recipientAccNum){
                    cout << "\nCannot transfer to the same account!" << endl;
                    break;
                }
                
                sender->transfer(*recipient);
                break;
            }
            
            case 5: {
                // Apply interest to an account
                if(accounts.empty()){
                    cout << "\nNo accounts available. Please create an account first." << endl;
                    break;
                }
                
                cout << "\nEnter account number to apply interest: ";
                int accNum = getValidIntInput();
                SavingsAccount* account = findAccount(accounts, accNum);
                
                if(account){
                    account->applyInterest();
                } else {
                    cout << "\nAccount not found!" << endl;
                }
                break;
            }
            
            case 6: {
                // View specific account details
                if(accounts.empty()){
                    cout << "\nNo accounts available. Please create an account first." << endl;
                    break;
                }
                
                cout << "\nEnter account number to view details: ";
                int accNum = getValidIntInput();
                SavingsAccount* account = findAccount(accounts, accNum);
                
                if(account){
                    account->ShowInfo();
                } else {
                    cout << "\nAccount not found!" << endl;
                }
                break;
            }
            
            case 7: {
                // View all accounts summary
                displayAllAccounts(accounts);
                break;
            }
            
            case 8: {
                // Exit program
                cout << "\nThank you for using our banking system!" << endl;
                cout << "Closing all accounts..." << endl;
                break;
            }
            
            default: {
                cout << "\nInvalid choice! Please select a number between 1 and 8." << endl;
                break;
            }
        }
        
    } while(choice != 8); // Continue until user chooses to exit
    
    return 0;
}