const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const tileSize = 20;
const rows = canvas.height / tileSize;
const cols = canvas.width / tileSize;

let snake = [
    { x: 2 * tileSize, y: 2 * tileSize },
    { x: 1 * tileSize, y: 2 * tileSize },
    { x: 0 * tileSize, y: 2 * tileSize }
];

let food = { x: 10 * tileSize, y: 10 * tileSize };
let direction = 'right';
let changingDirection = false;
let score = 0;
let dx = tileSize;
let dy = 0;

document.addEventListener('keydown', changeDirection);
document.getElementById('up').addEventListener('click', () => changeDirection({ key: 'ArrowUp' }));
document.getElementById('down').addEventListener('click', () => changeDirection({ key: 'ArrowDown' }));
document.getElementById('left').addEventListener('click', () => changeDirection({ key: 'ArrowLeft' }));
document.getElementById('right').addEventListener('click', () => changeDirection({ key: 'ArrowRight' }));

function gameLoop() {
    if (didGameEnd()) return;

    changingDirection = false;
    clearCanvas();
    drawFood();
    moveSnake();
    drawSnake();

    setTimeout(gameLoop, 100);
}

function clearCanvas() {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawSnake() {
    ctx.fillStyle = 'lightgreen';
    ctx.strokeStyle = 'darkgreen';
    snake.forEach(snakePart => {
        ctx.fillRect(snakePart.x, snakePart.y, tileSize, tileSize);
        ctx.strokeRect(snakePart.x, snakePart.y, tileSize, tileSize);
    });
}

function drawFood() {
    ctx.fillStyle = 'red';
    ctx.fillRect(food.x, food.y, tileSize, tileSize);
}

function moveSnake() {
    const head = { x: snake[0].x + dx, y: snake[0].y + dy };
    snake.unshift(head);

    if (snake[0].x === food.x && snake[0].y === food.y) {
        score += 10;
        createFood();
    } else {
        snake.pop();
    }
}

function createFood() {
    food.x = Math.floor(Math.random() * cols) * tileSize;
    food.y = Math.floor(Math.random() * rows) * tileSize;

    snake.forEach(part => {
        if (part.x === food.x && part.y === food.y) createFood();
    });
}

function changeDirection(event) {
    if (changingDirection) return;
    changingDirection = true;

    const keyPressed = event.key;
    const goingUp = dy === -tileSize;
    const goingDown = dy === tileSize;
    const goingRight = dx === tileSize;
    const goingLeft = dx === -tileSize;

    if (keyPressed === 'ArrowUp' && !goingDown) {
        dx = 0;
        dy = -tileSize;
    }

    if (keyPressed === 'ArrowDown' && !goingUp) {
        dx = 0;
        dy = tileSize;
    }

    if (keyPressed === 'ArrowLeft' && !goingRight) {
        dx = -tileSize;
        dy = 0;
    }

    if (keyPressed === 'ArrowRight' && !goingLeft) {
        dx = tileSize;
        dy = 0;
    }
}

function didGameEnd() {
    for (let i = 4; i < snake.length; i++) {
        if (snake[i].x === snake[0].x && snake[i].y === snake[0].y) return true;
    }

    const hitLeftWall = snake[0].x < 0;
    const hitRightWall = snake[0].x >= canvas.width;
    const hitTopWall = snake[0].y < 0;
    const hitBottomWall = snake[0].y >= canvas.height;

    return hitLeftWall || hitRightWall || hitTopWall || hitBottomWall;
}

createFood();
gameLoop();
