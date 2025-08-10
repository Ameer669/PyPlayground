#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <iomanip>
#include <ctime>
#include <algorithm>
#include <limits>
#include <sstream>

// Class to handle date and time operations
class DateTime {
private:
    std::time_t currentTime;
    std::tm* timeInfo;
    
public:
    DateTime() {
        currentTime = std::time(nullptr);
        timeInfo = std::localtime(&currentTime);
    }
    
    std::string getFormattedDateTime() {
        char buffer[80];
        std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeInfo);
        return std::string(buffer);
    }
    
    std::string getFormattedDate() {
        char buffer[80];
        std::strftime(buffer, sizeof(buffer), "%Y-%m-%d", timeInfo);
        return std::string(buffer);
    }
};

// Class to represent a transaction
class Transaction {
private:
    std::string date;
    std::string type;
    double amount;
    std::string description;
    double balanceAfter;
    
public:
    Transaction(std::string type, double amount, std::string description, double balanceAfter)
        : type(type), amount(amount), description(description), balanceAfter(balanceAfter) {
        DateTime dt;
        date = dt.getFormattedDateTime();
    }
    
    // Constructor for loading from file
    Transaction(std::string date, std::string type, double amount, std::string description, double balanceAfter)
        : date(date), type(type), amount(amount), description(description), balanceAfter(balanceAfter) {}
    
    std::string getDate() const { return date; }
    std::string getType() const { return type; }
    double getAmount() const { return amount; }
    std::string getDescription() const { return description; }
    double getBalanceAfter() const { return balanceAfter; }
    
    // Format transaction for display
    std::string toString() const {
        std::ostringstream oss;
        oss << std::left << std::setw(20) << date;
        oss << std::left << std::setw(15) << type;
        oss << std::right << std::setw(12) << std::fixed << std::setprecision(2) << amount;
        oss << std::left << std::setw(25) << " " + description;
        oss << std::right << std::setw(12) << std::fixed << std::setprecision(2) << balanceAfter;
        return oss.str();
    }
    
    // Format transaction for saving to file
    std::string toFileString() const {
        std::ostringstream oss;
        oss << date << "," << type << "," << amount << "," << description << "," << balanceAfter;
        return oss.str();
    }
};

// Class to represent a bank account
class Account {
private:
    std::string accountId;
    std::string name;
    std::string password;
    double balance;
    std::vector<Transaction> transactions;
    
public:
    Account(std::string accountId, std::string name, std::string password, double initialDeposit = 0.0)
        : accountId(accountId), name(name), password(password), balance(initialDeposit) {
        if (initialDeposit > 0) {
            addTransaction("DEPOSIT", initialDeposit, "Initial deposit", balance);
        }
    }
    
    std::string getAccountId() const { return accountId; }
    std::string getName() const { return name; }
    double getBalance() const { return balance; }
    
    // Verify if password is correct
    bool verifyPassword(const std::string& inputPassword) const {
        return password == inputPassword;
    }
    
    // Add transaction to history
    void addTransaction(std::string type, double amount, std::string description, double balanceAfter) {
        transactions.push_back(Transaction(type, amount, description, balanceAfter));
    }
    
    // Load transaction from file
    void loadTransaction(std::string date, std::string type, double amount, std::string description, double balanceAfter) {
        transactions.push_back(Transaction(date, type, amount, description, balanceAfter));
    }
    
    // Deposit money
    bool deposit(double amount) {
        if (amount <= 0) {
            return false;
        }
        
        balance += amount;
        addTransaction("DEPOSIT", amount, "Cash deposit", balance);
        return true;
    }
    
    // Withdraw money
    bool withdraw(double amount) {
        if (amount <= 0 || amount > balance) {
            return false;
        }
        
        balance -= amount;
        addTransaction("WITHDRAW", -amount, "Cash withdrawal", balance);
        return true;
    }
    
    // Transfer money to another account
    bool transfer(Account& recipient, double amount) {
        if (amount <= 0 || amount > balance) {
            return false;
        }
        
        balance -= amount;
        recipient.balance += amount;
        
        addTransaction("TRANSFER OUT", -amount, "Transfer to " + recipient.accountId, balance);
        recipient.addTransaction("TRANSFER IN", amount, "Transfer from " + accountId, recipient.balance);
        
        return true;
    }
    
    // Display account information
    void displayInfo() const {
        std::cout << "\n╔═══════════════════════════════════════╗" << std::endl;
        std::cout << "║ Account Information                   ║" << std::endl;
        std::cout << "╠═══════════════════════════════════════╣" << std::endl;
        std::cout << "║ Account ID: " << std::left << std::setw(24) << accountId << "║" << std::endl;
        std::cout << "║ Account Holder: " << std::left << std::setw(20) << name << "║" << std::endl;
        std::cout << "║ Current Balance: $" << std::left << std::setw(19) << std::fixed << std::setprecision(2) << balance << "║" << std::endl;
        std::cout << "╚═══════════════════════════════════════╝" << std::endl;
    }
    
    // Display transaction history
    void displayTransactionHistory() const {
        if (transactions.empty()) {
            std::cout << "\nNo transactions found for this account." << std::endl;
            return;
        }
        
        std::cout << "\n╔═══════════════════════════════════════════════════════════╗" << std::endl;
        std::cout << "║ Transaction History                                                                    ║" << std::endl;
        std::cout << "╠════════════════════════════════════════════════════════════╣" << std::endl;
        std::cout << "║ " << std::left << std::setw(20) << "Date & Time";
        std::cout << std::left << std::setw(15) << "Type";
        std::cout << std::right << std::setw(12) << "Amount";
        std::cout << std::left << std::setw(25) << " Description";
        std::cout << std::right << std::setw(12) << "Balance    ║" << std::endl;
        std::cout << "╠════════════════════════════════════════════════════════════╣" << std::endl;
        
        for (const auto& transaction : transactions) {
            std::cout << "║ " << transaction.toString() << " ║" << std::endl;
        }
        
        std::cout << "╚════════════════════════════════════════════════════════════╝" << std::endl;
    }
    
    // Save transactions to file
    void saveTransactionsToFile() const {
        std::ofstream outFile("transactions_" + accountId + ".txt");
        if (!outFile) {
            std::cerr << "Error: Unable to open transaction file for writing." << std::endl;
            return;
        }
        
        for (const auto& transaction : transactions) {
            outFile << transaction.toFileString() << std::endl;
        }
        
        outFile.close();
    }
    
    // Load transactions from file
    void loadTransactionsFromFile() {
        std::ifstream inFile("transactions_" + accountId + ".txt");
        if (!inFile) {
            // No transaction file exists yet, which is fine for new accounts
            return;
        }
        
        transactions.clear();
        
        std::string line;
        while (std::getline(inFile, line)) {
            std::istringstream iss(line);
            std::string date, type, description;
            double amount, balanceAfter;
            
            // Parse the comma-separated values
            std::getline(iss, date, ',');
            std::getline(iss, type, ',');
            iss >> amount;
            iss.ignore(); // Skip the comma
            std::getline(iss, description, ',');
            iss >> balanceAfter;
            
            loadTransaction(date, type, amount, description, balanceAfter);
        }
        
        inFile.close();
        
        // Update balance based on the last transaction
        if (!transactions.empty()) {
            balance = transactions.back().getBalanceAfter();
        }
    }
    
    // Format account data for saving to file
    std::string toFileString() const {
        std::ostringstream oss;
        oss << accountId << "," << name << "," << password << "," << balance;
        return oss.str();
    }
};

// Class to manage the banking system
class BankSystem {
private:
    std::vector<Account> accounts;
    Account* currentAccount;
    
    // Generate a unique account ID
    std::string generateAccountId() {
        std::string prefix = "ACC";
        DateTime dt;
        std::string timestamp = dt.getFormattedDate();
        timestamp.erase(std::remove(timestamp.begin(), timestamp.end(), '-'), timestamp.end());
        
        // Add a random suffix (3 digits)
        int randomSuffix = rand() % 1000;
        std::ostringstream oss;
        oss << prefix << timestamp << std::setw(3) << std::setfill('0') << randomSuffix;
        
        return oss.str();
    }
    
    // Save all accounts to file
    void saveAccountsToFile() {
        std::ofstream outFile("accounts.txt");
        if (!outFile) {
            std::cerr << "Error: Unable to open accounts file for writing." << std::endl;
            return;
        }
        
        for (const auto& account : accounts) {
            outFile << account.toFileString() << std::endl;
            account.saveTransactionsToFile();
        }
        
        outFile.close();
    }
    
    // Load all accounts from file
    void loadAccountsFromFile() {
        std::ifstream inFile("accounts.txt");
        if (!inFile) {
            // No account file exists yet
            return;
        }
        
        accounts.clear();
        
        std::string line;
        while (std::getline(inFile, line)) {
            std::istringstream iss(line);
            std::string accountId, name, password;
            double balance;
            
            // Parse the comma-separated values
            std::getline(iss, accountId, ',');
            std::getline(iss, name, ',');
            std::getline(iss, password, ',');
            iss >> balance;
            
            accounts.push_back(Account(accountId, name, password, balance));
            accounts.back().loadTransactionsFromFile();
        }
        inFile.close();
    }
    
    // Find account by ID
    Account* findAccountById(const std::string& accountId) {
        for (auto& account : accounts) {
            if (account.getAccountId() == accountId) {
                return &account;
            }
        }
        return nullptr;
    }
public:
    BankSystem() : currentAccount(nullptr) {
        // Seed the random number generator
        srand(static_cast<unsigned int>(time(nullptr)));
        
        // Load existing accounts from file
        loadAccountsFromFile();
    }
    
    ~BankSystem() {
        // Save accounts before exiting
        saveAccountsToFile();
    }
    
    // Create a new account
    bool createAccount(const std::string& name, const std::string& password, double initialDeposit = 0.0) {
        if (name.empty() || password.empty() || initialDeposit < 0) {
            return false;
        }
        
        std::string accountId = generateAccountId();
        accounts.push_back(Account(accountId, name, password, initialDeposit));
        saveAccountsToFile();
        
        std::cout << "\nAccount created successfully!" << std::endl;
        std::cout << "Your Account ID is: " << accountId << std::endl;
        std::cout << "Please remember this ID for login purposes." << std::endl;
        
        return true;
    }
    
    // Login to an account
    bool login(const std::string& accountId, const std::string& password) {
        Account* account = findAccountById(accountId);
        
        if (account && account->verifyPassword(password)) {
            currentAccount = account;
            std::cout << "\nLogin successful! Welcome, " << account->getName() << "!" << std::endl;
            return true;
        }
        
        std::cout << "\nLogin failed! Invalid account ID or password." << std::endl;
        return false;
    }
    
    // Logout from current account
    void logout() {
        if (currentAccount) {
            std::cout << "\nLogout successful. Goodbye, " << currentAccount->getName() << "!" << std::endl;
            currentAccount = nullptr;
        }
    }
    
    // Check if user is logged in
    bool isLoggedIn() const {
        return currentAccount != nullptr;
    }
    
    // Display current account information
    void displayCurrentAccountInfo() const {
        if (currentAccount) {
            currentAccount->displayInfo();
        } else {
            std::cout << "\nNo account is currently logged in." << std::endl;
        }
    }
    
    // Deposit money into current account
    bool deposit(double amount) {
        if (!currentAccount) {
            std::cout << "\nNo account is currently logged in." << std::endl;
            return false;
        }
        
        if (currentAccount->deposit(amount)) {
            std::cout << "\nDeposit successful. New balance: $" << std::fixed << std::setprecision(2) << currentAccount->getBalance() << std::endl;
            saveAccountsToFile();
            return true;
        } else {
            std::cout << "\nDeposit failed. Please enter a valid amount." << std::endl;
            return false;
        }
    }
    
    // Withdraw money from current account
    bool withdraw(double amount) {
        if (!currentAccount) {
            std::cout << "\nNo account is currently logged in." << std::endl;
            return false;
        }
        
        if (currentAccount->withdraw(amount)) {
            std::cout << "\nWithdrawal successful. New balance: $" << std::fixed << std::setprecision(2) << currentAccount->getBalance() << std::endl;
            saveAccountsToFile();
            return true;
        } else {
            std::cout << "\nWithdrawal failed. Please check your balance and enter a valid amount." << std::endl;
            return false;
        }
    }
    
    // Transfer money to another account
    bool transfer(const std::string& recipientId, double amount) {
        if (!currentAccount) {
            std::cout << "\nNo account is currently logged in." << std::endl;
            return false;
        }
        
        if (currentAccount->getAccountId() == recipientId) {
            std::cout << "\nYou cannot transfer money to your own account." << std::endl;
            return false;
        }
        
        Account* recipientAccount = findAccountById(recipientId);
        if (!recipientAccount) {
            std::cout << "\nRecipient account not found." << std::endl;
            return false;
        }
        
        if (currentAccount->transfer(*recipientAccount, amount)) {
            std::cout << "\nTransfer successful. New balance: $" << std::fixed << std::setprecision(2) << currentAccount->getBalance() << std::endl;
            saveAccountsToFile();
            return true;
        } else {
            std::cout << "\nTransfer failed. Please check your balance and enter a valid amount." << std::endl;
            return false;
        }
    }
    
    // Display transaction history for current account
    void displayTransactionHistory() const {
        if (!currentAccount) {
            std::cout << "\nNo account is currently logged in." << std::endl;
            return;
        }
        
        currentAccount->displayTransactionHistory();
    }
    
    // Display all accounts (for admin purposes)
    void displayAllAccounts() const {
        if (accounts.empty()) {
            std::cout << "\nNo accounts found in the system." << std::endl;
            return;
        }
        
        std::cout << "\n╔════════════════════════════════════════════════════════════╗" << std::endl;
        std::cout << "║ All Accounts                                                ║" << std::endl;
        std::cout << "╠════════════════════════════════════════════════════════════╣" << std::endl;
        std::cout << "║ " << std::left << std::setw(15) << "Account ID";
        std::cout << std::left << std::setw(25) << "Account Holder";
        std::cout << std::right << std::setw(15) << "Balance    ║" << std::endl;
        std::cout << "╠════════════════════════════════════════════════════════════╣" << std::endl;
        
        for (const auto& account : accounts) {
            std::cout << "║ " << std::left << std::setw(15) << account.getAccountId();
            std::cout << std::left << std::setw(25) << account.getName();
            std::cout << std::right << std::setw(15) << std::fixed << std::setprecision(2) << account.getBalance() << " ║" << std::endl;
        }
        
        std::cout << "╚════════════════════════════════════════════════════════════╝" << std::endl;
    }
};

// Function declarations for menus
void displayMainMenu(BankSystem& bank);
void displayLoggedInMenu(BankSystem& bank);

// Utility functions for input validation
namespace Utils {
    // Clear the input buffer
    void clearInputBuffer() {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
    
    // Get a valid double input
    double getValidDoubleInput(const std::string& prompt) {
        double value;
        bool validInput = false;
        
        do {
            std::cout << prompt;
            std::cin >> value;
            
            if (std::cin.fail() || value < 0) {
                std::cout << "Invalid input. Please enter a valid positive number." << std::endl;
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            } else {
                validInput = true;
            }
        } while (!validInput);
        
        clearInputBuffer();
        return value;
    }
    
    // Get a string input
    std::string getStringInput(const std::string& prompt) {
        std::string input;
        std::cout << prompt;
        std::getline(std::cin, input);
        return input;
    }
    
    // Display menu and get choice
    int displayMenuAndGetChoice(const std::vector<std::string>& menuOptions) {
        int choice;
        bool validInput = false;
        
        do {
            std::cout << "\n╔════════════════════════════════════╗" << std::endl;
            std::cout << "║ Menu Options                       ║" << std::endl;
            std::cout << "╠════════════════════════════════════╣" << std::endl;
            
            for (size_t i = 0; i < menuOptions.size(); ++i) {
                std::cout << "║ " << (i + 1) << ". " << std::left << std::setw(31) << menuOptions[i] << "║" << std::endl;
            }
            
            std::cout << "╚════════════════════════════════════╝" << std::endl;
            std::cout << "\nEnter your choice (1-" << menuOptions.size() << "): ";
            std::cin >> choice;
            
            if (std::cin.fail() || choice < 1 || choice > static_cast<int>(menuOptions.size())) {
                std::cout << "Invalid choice. Please try again." << std::endl;
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            } else {
                validInput = true;
            }
        } while (!validInput);
        
        clearInputBuffer();
        return choice;
    }
}

// Main menu when not logged in
void displayMainMenu(BankSystem& bank) {
    std::vector<std::string> menuOptions = {
        "Create a New Account",
        "Login",
        "Exit"
    };
    
    bool exitProgram = false;
    
    while (!exitProgram) {
        std::cout << "\n================= BANK SYSTEM =================" << std::endl;
        std::cout << "Welcome to the Bank Management System" << std::endl;
        
        int choice = Utils::displayMenuAndGetChoice(menuOptions);
        
        switch (choice) {
            case 1: { // Create a New Account
                std::string name = Utils::getStringInput("Enter your name: ");
                std::string password = Utils::getStringInput("Create a password: ");
                double initialDeposit = Utils::getValidDoubleInput("Enter initial deposit amount (0 for none): $");
                
                bank.createAccount(name, password, initialDeposit);
                break;
            }
            case 2: { // Login
                std::string accountId = Utils::getStringInput("Enter your Account ID: ");
                std::string password = Utils::getStringInput("Enter your password: ");
                
                if (bank.login(accountId, password)) {
                    displayLoggedInMenu(bank);
                }
                break;
            }
            case 3: // Exit
                exitProgram = true;
                std::cout << "\nThank you for using the Bank Management System!" << std::endl;
                break;
        }
    }
}

// Menu when logged in
void displayLoggedInMenu(BankSystem& bank) {
    std::vector<std::string> menuOptions = {
        "Account Information",
        "Deposit Money",
        "Withdraw Money",
        "Transfer Money",
        "Transaction History",
        "Logout"
    };
    
    bool logout = false;
    
    while (!logout && bank.isLoggedIn()) {
        std::cout << "\n================= ACCOUNT MENU =================" << std::endl;
        
        int choice = Utils::displayMenuAndGetChoice(menuOptions);
        
        switch (choice) {
            case 1: // Account Information
                bank.displayCurrentAccountInfo();
                break;
            case 2: { // Deposit Money
                double amount = Utils::getValidDoubleInput("Enter deposit amount: $");
                bank.deposit(amount);
                break;
            }
            case 3: { // Withdraw Money
                double amount = Utils::getValidDoubleInput("Enter withdrawal amount: $");
                bank.withdraw(amount);
                break;
            }
            case 4: { // Transfer Money
                std::string recipientId = Utils::getStringInput("Enter recipient's Account ID: ");
                double amount = Utils::getValidDoubleInput("Enter transfer amount: $");
                bank.transfer(recipientId, amount);
                break;
            }
            case 5: // Transaction History
                bank.displayTransactionHistory();
                break;
            case 6: // Logout
                bank.logout();
                logout = true;
                break;
        }
    }
}

// Main function
int main() {
    // Create the bank system
    BankSystem bank;
    
    // Display the main menu
    displayMainMenu(bank);
    
    return 0;
}
