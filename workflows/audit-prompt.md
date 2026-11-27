# Optional first step: audit the Reach Dog JSON

Before you hand a Reach Dog output to a workflow, you can ask your AI model to check it against your catalog and improve on it. Do it in a fresh chat, so the review starts with a clean context window: just your catalog and the JSON.

Attach your catalog CSV and the Reach Dog JSON, then paste:

```
Attached: my product catalog (CSV) and one output Reach Dog built from it (JSON). Before I use it, review it against my catalog and improve on it. Judge it for what it is, not for fields that come from other Reach Dog outputs. Start with a one-line verdict: ready to use as is, or ready after a few changes. Then, for each attribute it contains, check the values against my products and suggest improvements: anything missing, anything that doesn't fit, and anything that could be sharper, with a one-line reason each. If it's already thorough, say so and stop there. Make no health or safety claims.
```

You get a verdict and a list of suggested changes. Apply the ones you agree with, then run the workflow.

Want the model to apply the changes for you? Add this line to the end of the prompt:

```
Then write an improved copy of the JSON in the same structure, with your changes marked.
```

On a large output, such as a long keyword list, that copy can be long, so the suggestions alone are usually enough.
