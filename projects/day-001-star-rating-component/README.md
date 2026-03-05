# Star Rating Component

This project implements a simple, reusable Star Rating UI component using React and styled with Tailwind CSS. Users can hover over stars to preview a rating and click to select a final rating. It's a great beginner-friendly component to understand React state management and event handling, along with basic Tailwind CSS styling.

## Features

*   **Interactive Stars:** Hover to preview rating, click to set rating.
*   **Customizable:** Easily adjust the number of stars.
*   **Responsive:** Styled with Tailwind CSS for a modern look.

## Tech Stack

*   **Frontend:** React.js (JavaScript)
*   **Styling:** Tailwind CSS
*   **Build Tool:** Create React App (uses Node.js for development environment)

## Difficulty Level

Beginner

## Day Number

Day 1

## Getting Started

### Prerequisites

Make sure you have Node.js and npm installed on your machine.

### Installation

1.  **Clone the repository (or create a new project and copy files):**
    ```bash
    git clone <repository_url>
    cd star-rating-component
    ```
    If creating from scratch, initialize a new React project:
    ```bash
    npx create-react-app star-rating-component
    cd star-rating-component
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    ```
    *Note: `npx tailwindcss init -p` creates `tailwind.config.js` and `postcss.config.js`.*

3.  **Configure Tailwind CSS:**
    Update `tailwind.config.js` to include all your component files:
    ```javascript
    // tailwind.config.js
    module.exports = {
      content: [
        "./src/**/*.{js,jsx,ts,tsx}",
        "./public/index.html"
      ],
      theme: {
        extend: {},
      },
      plugins: [],
    }
    ```

4.  **Add Tailwind directives to your CSS:**
    Add the following to your `src/index.css` file:
    ```css
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
    ```

### Running the Application

To start the development server:

```bash
npm start
```

This will open the application in your browser at `http://localhost:3000` (or another available port).
