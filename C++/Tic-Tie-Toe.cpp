#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>

class TicTacToe {
private:
    std::vector<std::vector<char>> board;
    char currentPlayer;
    char humanPlayer;
    char aiPlayer;
    
public:
    // Constructor initializes the 3x3 board with empty spaces
    TicTacToe() : board(3, std::vector<char>(3, ' ')), currentPlayer('X'), humanPlayer('X'), aiPlayer('O') {}
    
    // Display the current state of the board with clear formatting
    void displayBoard() {
        std::cout << "\n  0   1   2\n";
        for (int i = 0; i < 3; i++) {
            std::cout << i << " ";
            for (int j = 0; j < 3; j++) {
                std::cout << board[i][j];
                if (j < 2) std::cout << " | ";
            }
            std::cout << "\n";
            if (i < 2) std::cout << "  ---------\n";
        }
        std::cout << "\n";
    }
    
    // Check if a move is valid (within bounds and cell is empty)
    bool isValidMove(int row, int col) {
        return row >= 0 && row < 3 && col >= 0 && col < 3 && board[row][col] == ' ';
    }
    
    // Make a move on the board
    void makeMove(int row, int col, char player) {
        if (isValidMove(row, col)) {
            board[row][col] = player;
        }
    }
    
    // Undo a move (useful for AI move analysis)
    void undoMove(int row, int col) {
        board[row][col] = ' ';
    }
    
    // Check for winning conditions - examines all possible winning lines
    char checkWinner() {
        // Check rows
        for (int i = 0; i < 3; i++) {
            if (board[i][0] == board[i][1] && board[i][1] == board[i][2] && board[i][0] != ' ') {
                return board[i][0];
            }
        }
        
        // Check columns
        for (int j = 0; j < 3; j++) {
            if (board[0][j] == board[1][j] && board[1][j] == board[2][j] && board[0][j] != ' ') {
                return board[0][j];
            }
        }
        
        // Check diagonals
        if (board[0][0] == board[1][1] && board[1][1] == board[2][2] && board[0][0] != ' ') {
            return board[0][0];
        }
        if (board[0][2] == board[1][1] && board[1][1] == board[2][0] && board[0][2] != ' ') {
            return board[0][2];
        }
        
        return ' '; // No winner yet
    }
    
    // Check if the board is full (tie condition)
    bool isBoardFull() {
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (board[i][j] == ' ') {
                    return false;
                }
            }
        }
        return true;
    }
    
    // Check if the game has ended (win or tie)
    bool isGameOver() {
        return checkWinner() != ' ' || isBoardFull();
    }
    
    // Minimax algorithm with alpha-beta pruning for optimal AI moves
    // This function evaluates all possible future game states
    int minimax(int depth, bool isMaximizing, int alpha, int beta) {
        char winner = checkWinner();
        
        // Base cases: game is over
        if (winner == aiPlayer) return 10 - depth;      // AI wins (prefer quicker wins)
        if (winner == humanPlayer) return depth - 10;   // Human wins (delay losses)
        if (isBoardFull()) return 0;                     // Tie game
        
        if (isMaximizing) {
            // AI's turn: try to maximize score
            int maxEval = std::numeric_limits<int>::min();
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++) {
                    if (isValidMove(i, j)) {
                        makeMove(i, j, aiPlayer);
                        int eval = minimax(depth + 1, false, alpha, beta);
                        undoMove(i, j);
                        maxEval = std::max(maxEval, eval);
                        alpha = std::max(alpha, eval);
                        if (beta <= alpha) break; // Alpha-beta pruning
                    }
                }
                if (beta <= alpha) break;
            }
            return maxEval;
        } else {
            // Human's turn: try to minimize score (from AI's perspective)
            int minEval = std::numeric_limits<int>::max();
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++) {
                    if (isValidMove(i, j)) {
                        makeMove(i, j, humanPlayer);
                        int eval = minimax(depth + 1, true, alpha, beta);
                        undoMove(i, j);
                        minEval = std::min(minEval, eval);
                        beta = std::min(beta, eval);
                        if (beta <= alpha) break; // Alpha-beta pruning
                    }
                }
                if (beta <= alpha) break;
            }
            return minEval;
        }
    }
    
    // Find the best move for the AI using minimax algorithm
    std::pair<int, int> getBestMove() {
        int bestScore = std::numeric_limits<int>::min();
        std::pair<int, int> bestMove = {-1, -1};
        
        // Evaluate every possible move
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (isValidMove(i, j)) {
                    makeMove(i, j, aiPlayer);
                    int score = minimax(0, false, std::numeric_limits<int>::min(), std::numeric_limits<int>::max());
                    undoMove(i, j);
                    
                    // Choose the move with the highest score
                    if (score > bestScore) {
                        bestScore = score;
                        bestMove = {i, j};
                    }
                }
            }
        }
        
        return bestMove;
    }
    
    // Get human player's move with input validation
    std::pair<int, int> getHumanMove() {
        int row, col;
        while (true) {
            std::cout << "Enter your move (row col): ";
            std::cin >> row >> col;
            
            if (std::cin.fail()) {
                std::cin.clear();
                std::cin.ignore(10000, '\n');
                std::cout << "Invalid input! Please enter two numbers.\n";
                continue;
            }
            
            if (isValidMove(row, col)) {
                return {row, col};
            } else {
                std::cout << "Invalid move! Try again.\n";
            }
        }
    }
    
    // Main game loop that handles turn-based gameplay
    void playGame() {
        std::cout << "=== Smart Tic Tac Toe ===\n";
        std::cout << "You are X, AI is O\n";
        std::cout << "Enter moves as: row column (0-2)\n";
        
        displayBoard();
        
        while (!isGameOver()) {
            if (currentPlayer == humanPlayer) {
                // Human's turn
                std::cout << "Your turn:\n";
                auto move = getHumanMove();
                makeMove(move.first, move.second, humanPlayer);
                currentPlayer = aiPlayer;
            } else {
                // AI's turn - analyze board and make strategic move
                std::cout << "AI is thinking...\n";
                auto bestMove = getBestMove();
                makeMove(bestMove.first, bestMove.second, aiPlayer);
                std::cout << "AI chose position (" << bestMove.first << ", " << bestMove.second << ")\n";
                currentPlayer = humanPlayer;
            }
            
            displayBoard();
        }
        
        // Display game results
        char winner = checkWinner();
        if (winner == humanPlayer) {
            std::cout << "Congratulations! You won!\n";
        } else if (winner == aiPlayer) {
            std::cout << "AI wins! Better luck next time.\n";
        } else {
            std::cout << "It's a tie! Well played.\n";
        }
    }
};

int main() {
    TicTacToe game;
    game.playGame();
    
    return 0;
}