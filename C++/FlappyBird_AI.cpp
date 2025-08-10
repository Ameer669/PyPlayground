// FlappyBird.cpp
// A simple Flappy Bird clone using SFML
// Compile with: g++ -o FlappyBird FlappyBird.cpp -lsfml-graphics -lsfml-window -lsfml-system

#include <SFML/Graphics.hpp>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <iostream>

const int WINDOW_WIDTH = 800;
const int WINDOW_HEIGHT = 600;
const float GRAVITY = 0.25f;
const float JUMP_FORCE = -7.0f;
const float PIPE_SPEED = 3.0f;
const int PIPE_SPAWN_TIME = 1500; // milliseconds
const int PIPE_GAP = 200;
const int PIPE_WIDTH = 70;

// Bird class
class Bird {
public:
    sf::RectangleShape shape;
    float velocity;
    bool isAlive;

    Bird() {
        shape.setSize(sf::Vector2f(40, 30));
        shape.setFillColor(sf::Color::Yellow);
        shape.setPosition(100, WINDOW_HEIGHT / 2);
        velocity = 0;
        isAlive = true;
    }

    void update() {
        velocity += GRAVITY;
        shape.move(0, velocity);

        // Keep the bird on screen
        if (shape.getPosition().y < 0) {
            shape.setPosition(shape.getPosition().x, 0);
            velocity = 0;
        }

        // Check if bird hits the ground
        if (shape.getPosition().y + shape.getSize().y > WINDOW_HEIGHT) {
            shape.setPosition(shape.getPosition().x, WINDOW_HEIGHT - shape.getSize().y);
            isAlive = false;
        }
    }

    void jump() {
        velocity = JUMP_FORCE;
    }
};

// Pipe class
class Pipe {
public:
    sf::RectangleShape topPipe;
    sf::RectangleShape bottomPipe;
    bool passed;

    Pipe(float x) {
        int gapPosition = rand() % (WINDOW_HEIGHT - PIPE_GAP - 100) + 50;

        topPipe.setSize(sf::Vector2f(PIPE_WIDTH, gapPosition));
        topPipe.setFillColor(sf::Color::Green);
        topPipe.setPosition(x, 0);

        bottomPipe.setSize(sf::Vector2f(PIPE_WIDTH, WINDOW_HEIGHT - gapPosition - PIPE_GAP));
        bottomPipe.setFillColor(sf::Color::Green);
        bottomPipe.setPosition(x, gapPosition + PIPE_GAP);

        passed = false;
    }

    void update() {
        topPipe.move(-PIPE_SPEED, 0);
        bottomPipe.move(-PIPE_SPEED, 0);
    }

    bool isOffScreen() {
        return topPipe.getPosition().x + topPipe.getSize().x < 0;
    }

    bool checkCollision(const Bird& bird) {
        return bird.shape.getGlobalBounds().intersects(topPipe.getGlobalBounds()) ||
               bird.shape.getGlobalBounds().intersects(bottomPipe.getGlobalBounds());
    }
};

// Game class
class Game {
public:
    sf::RenderWindow window;
    Bird bird;
    std::vector<Pipe> pipes;
    sf::Clock pipeSpawnClock;
    sf::Font font;
    sf::Text scoreText;
    sf::Text gameOverText;
    int score;
    bool gameOver;

    Game() : window(sf::VideoMode(WINDOW_WIDTH, WINDOW_HEIGHT), "Flappy Bird") {
        window.setFramerateLimit(60);
        srand(static_cast<unsigned int>(time(nullptr)));
        
        // Load font
        if (!font.loadFromFile("arial.ttf")) {
            // If font loading fails, just print an error
            std::cerr << "Failed to load font" << std::endl;
        }
        
        // Setup score text
        scoreText.setFont(font);
        scoreText.setCharacterSize(30);
        scoreText.setFillColor(sf::Color::White);
        scoreText.setPosition(10, 10);
        
        // Setup game over text
        gameOverText.setFont(font);
        gameOverText.setString("Game Over! Press R to restart");
        gameOverText.setCharacterSize(40);
        gameOverText.setFillColor(sf::Color::Red);
        gameOverText.setPosition(WINDOW_WIDTH / 2 - 200, WINDOW_HEIGHT / 2 - 20);
        
        score = 0;
        gameOver = false;
    }

    void run() {
        while (window.isOpen()) {
            handleEvents();
            
            if (!gameOver) {
                update();
            }
            
            render();
        }
    }

private:
    void handleEvents() {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
            }
            
            if (event.type == sf::Event::KeyPressed) {
                if (event.key.code == sf::Keyboard::Space && !gameOver) {
                    bird.jump();
                }
                
                if (event.key.code == sf::Keyboard::R && gameOver) {
                    restart();
                }
            }
        }
    }

    void update() {
        // Update bird
        bird.update();
        
        // Spawn pipes
        if (pipeSpawnClock.getElapsedTime().asMilliseconds() > PIPE_SPAWN_TIME) {
            pipes.push_back(Pipe(WINDOW_WIDTH));
            pipeSpawnClock.restart();
        }
        
        // Update pipes and check collisions
        for (auto& pipe : pipes) {
            pipe.update();
            
            // Check collision
            if (pipe.checkCollision(bird)) {
                bird.isAlive = false;
                gameOver = true;
            }
            
            // Check if bird passed the pipe
            if (!pipe.passed && bird.shape.getPosition().x > pipe.topPipe.getPosition().x + pipe.topPipe.getSize().x) {
                pipe.passed = true;
                score++;
                scoreText.setString("Score: " + std::to_string(score));
            }
        }
        
        // Remove off-screen pipes
        for (auto it = pipes.begin(); it != pipes.end(); ) {
            if (it->isOffScreen()) {
                it = pipes.erase(it);
            } else {
                ++it;
            }
        }
        
        // Check if bird is alive
        if (!bird.isAlive) {
            gameOver = true;
        }
    }

    void render() {
        window.clear(sf::Color(135, 206, 235)); // Sky blue
        
        // Draw bird
        window.draw(bird.shape);
        
        // Draw pipes
        for (const auto& pipe : pipes) {
            window.draw(pipe.topPipe);
            window.draw(pipe.bottomPipe);
        }
        
        // Draw score
        window.draw(scoreText);
        
        // Draw game over text
        if (gameOver) {
            window.draw(gameOverText);
        }
        
        window.display();
    }

    void restart() {
        bird = Bird();
        pipes.clear();
        score = 0;
        scoreText.setString("Score: 0");
        gameOver = false;
        pipeSpawnClock.restart();
    }
};

// Main function
int main() {
    Game game;
    game.run();
    return 0;
}