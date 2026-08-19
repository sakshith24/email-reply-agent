
# Email Reply Agent

## Project Overview

Build an AI-powered email reply agent that connects to Gmail, reads incoming emails from the user's primary inbox, understands the email content, retrieves relevant information from a knowledge base, and generates a draft reply.

The user must be able to review and modify the AI-generated draft before sending it.

The application should maintain a record of incoming emails, generated drafts, and final sent replies.

---

## Core Objective

The system should:

1. Connect to Gmail using the Gmail API.
2. Fetch emails from the user's primary inbox.
3. Identify emails that require a response.
4. Extract and understand the relevant information from the email.
5. Retrieve relevant knowledge from Supabase.
6. Generate a context-aware reply using an LLM.
7. Present the generated reply to the user for review.
8. Allow the user to modify the draft.
9. Send the final reply through Gmail.
10. Store the original email, AI-generated draft, modified draft, and final sent reply in Supabase.

---

## Technology Requirements

### Email

Use the Gmail API for:

* Reading emails
* Reading email metadata
* Reading email threads
* Creating reply drafts
* Sending replies

Do not use browser automation for Gmail.

---

### LLM

The application should support an LLM provider such as:

* OpenAI API
* Gemini API

The LLM provider should be implemented in a way that allows the provider to be changed without rewriting the rest of the application.

Do not hard-code API keys or credentials.

Use environment variables for all secrets.

---

### Database

Use Supabase as the primary database.

Supabase should store the application's knowledge base and email-related information.

The knowledge base may contain information about:

* Courses
* Programs
* Products
* Services
* FAQs
* Policies
* Important dates
* Other information required to answer incoming emails

---

## Knowledge Retrieval

Incoming emails may contain questions about courses or programs.

Before generating a response, the agent should retrieve relevant information from the knowledge base.

The generated response should be grounded in the retrieved information.

The agent should not invent information that is not present in the available knowledge.

If the required information cannot be found, the system should clearly indicate that the information is unavailable rather than hallucinating an answer.

---

## Email Reply Generation

The reply-generation process should consider:

* Original email content
* Sender information
* Email thread/context
* Relevant retrieved knowledge
* Appropriate professional tone

The generated reply should be concise, useful, and directly address the sender's question.

The system should preserve important context from the original email.

---

## Human-in-the-Loop Requirement

AI-generated replies must NOT automatically be sent without user review.

The workflow should be:

```text
Incoming Email
      ↓
Email Analysis
      ↓
Knowledge Retrieval
      ↓
AI Reply Generation
      ↓
Draft Reply
      ↓
User Review
      ↓
User Modification (optional)
      ↓
User Approval
      ↓
Send Through Gmail
```

The user must have the ability to modify the AI-generated draft before sending it.

The final message sent to the recipient must be the user-approved version.

---

## Data Storage

Store the following information in Supabase where appropriate:

### Incoming Email

* Gmail message ID
* Thread ID
* Sender
* Recipient
* Subject
* Original email body
* Received timestamp

### AI Draft

* Generated reply
* LLM/provider used
* Generation timestamp
* Relevant retrieved knowledge

### Final Reply

* Final user-approved reply
* Sent timestamp
* Gmail message ID
* Whether the reply was modified by the user

The system should make it possible to distinguish between:

```text
Original Email
AI Generated Draft
User Modified Draft
Final Sent Reply
```

---

## Project Architecture

Prefer a modular architecture.

Separate the application into logical components such as:

```text
app/
├── gmail/
│   ├── client.py
│   ├── authentication.py
│   └── service.py
│
├── llm/
│   ├── openai.py
│   ├── gemini.py
│   └── prompts.py
│
├── knowledge/
│   ├── retrieval.py
│   └── embeddings.py
│
├── database/
│   ├── supabase.py
│   └── models.py
│
├── agent/
│   ├── workflow.py
│   └── reply_generator.py
│
├── api/
│   └── routes.py
│
└── main.py
```

The exact structure can evolve as the project grows, but responsibilities should remain separated.

---

## Agent Workflow

The agent should eventually follow a structured workflow:

```text
1. Fetch email
2. Parse email
3. Determine whether a response is required
4. Understand the user's question
5. Retrieve relevant knowledge
6. Generate a grounded response
7. Create a draft
8. Wait for human approval
9. Apply user modifications
10. Send the final reply
11. Store the result
```

Do not make the agent unnecessarily autonomous.

Human approval is required before sending an email.

---

## Context and Retrieval

When generating a reply, provide the LLM only the relevant context required to answer the email.

Avoid sending the entire knowledge base to the model when retrieval can identify the relevant information.

The retrieved context should be clearly separated from the user's email.

Example:

```text
SYSTEM INSTRUCTIONS

EMAIL:
<incoming email>

RELEVANT KNOWLEDGE:
<retrieved knowledge>

TASK:
Generate a professional reply to the email using the relevant knowledge.
```

---

## Security Rules

Never commit:

* API keys
* Gmail OAuth credentials
* Supabase keys
* `.env` files
* OAuth tokens
* Private user information

Use environment variables.

The `.env` file must be included in `.gitignore`.

Gmail access should follow the minimum permissions required by the application.

---

## Development Rules

Before implementing a new feature:

1. Inspect the existing project structure.
2. Reuse existing utilities where appropriate.
3. Avoid unnecessary dependencies.
4. Keep modules small and focused.
5. Do not rewrite working components unnecessarily.
6. Add error handling around external APIs.
7. Validate API responses.
8. Keep secrets out of source code.
9. Write testable functions.
10. Update documentation when architecture or behavior changes.

---

## LLM Rules

The LLM must not:

* Invent course information.
* Invent program details.
* Invent prices, dates, policies, or eligibility requirements.
* Claim that an action was completed when it was not.
* Send an email without explicit user approval.

If the knowledge base does not contain enough information to answer a question, the agent should indicate that additional information is required.

---

## Error Handling

Handle failures gracefully.

Important failure cases include:

* Gmail authentication failure
* Gmail API failure
* Invalid email data
* Supabase connection failure
* Missing knowledge
* LLM API failure
* Invalid LLM response
* Email sending failure

Do not silently ignore errors.

The user should receive a meaningful error message when an operation fails.

---

## Development Priority

Build the project incrementally.

### Phase 1

Gmail authentication and email fetching.

### Phase 2

Supabase database and knowledge storage.

### Phase 3

Knowledge retrieval.

### Phase 4

LLM reply generation.

### Phase 5

Draft review and editing.

### Phase 6

Gmail reply sending.

### Phase 7

Persistent email/draft/sent-message history.

### Phase 8

Agent workflow and improved automation.

### Phase 9

Testing, observability, security, and deployment.

---

## Important Principle

This project is a human-in-the-loop AI email assistant.

The AI should assist with understanding emails and drafting responses, while the user retains control over the final message and sending action.