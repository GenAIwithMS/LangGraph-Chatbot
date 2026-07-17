# MCP Evals

A Node.js package and GitHub Action for evaluating MCP (Model Context Protocol) tool implementations using LLM-based scoring. This helps ensure your MCP server's tools are working correctly and performing well.

## Installation

### As a Node.js Package

```bash
npm install mcp-evals
```

### As a GitHub Action

Add the following to your workflow file:

```yaml
name: Run MCP Evaluations
on:
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: npm install
        
      - name: Run MCP Evaluations
        uses: mclenhard/mcp-evals@v1.0.9
        with:
          evals_path: 'src/evals/evals.ts'
          server_path: 'src/index.ts'
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          model: 'gpt-4'  # Optional, defaults to gpt-4
```

## Usage

### 1. Create Your Evaluation File


Create a file (e.g., `evals.ts`) that exports your evaluation configuration:

```typescript
import { EvalConfig } from 'mcp-evals';
import { openai } from "@ai-sdk/openai";
import { grade, EvalFunction} from "mcp-evals";

const weatherEval: EvalFunction = {
    name: 'Weather Tool Evaluation',
    description: 'Evaluates the accuracy and completeness of weather information retrieval',
    run: async () => {
      const result = await grade(openai("gpt-4"), "What is the weather in New York?");
      return JSON.parse(result);
    }
};
const config: EvalConfig = {
    model: openai("gpt-4"),
    evals: [weatherEval]
  };
  
  export default config;
  
  export const evals = [
    weatherEval,
    // add other evals here
]; 
```

### 2. Run the Evaluations

#### As a Node.js Package

You can run the evaluations using the CLI:

```bash
npx mcp-eval path/to/your/evals.ts path/to/your/server.ts
```

#### As a GitHub Action

The action will automatically:
1. Run your evaluations
2. Post the results as a comment on the PR
3. Update the comment if the PR is updated

## Evaluation Results

Each evaluation returns an object with the following structure:

```typescript
interface EvalResult {
  accuracy: number;        // Score from 1-5
  completeness: number;    // Score from 1-5
  relevance: number;       // Score from 1-5
  clarity: number;         // Score from 1-5
  reasoning: number;       // Score from 1-5
  overall_comments: string; // Summary of strengths and weaknesses
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Evaluation Configuration

The `EvalConfig` interface requires:

- `model`: The language model to use for evaluation (e.g., GPT-4)
- `evals`: Array of evaluation functions to run

Each evaluation function must implement:

- `name`: Name of the evaluation
- `description`: Description of what the evaluation tests
- `run`: Async function that takes a model and returns an `EvalResult`

## License

MIT 