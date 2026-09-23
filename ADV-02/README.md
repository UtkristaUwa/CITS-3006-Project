# ADV-02 — AI Prompt Injection

## Category
Advanced — AI-related vulnerability

## Objective
Recover protected training information by exploiting a prompt-injection vulnerability in an AI support assistant.

## Vulnerability
The application places untrusted user input directly into the assistant's instruction context. The resulting instruction hierarchy can be manipulated by a crafted prompt that overrides the intended restrictions.

## Intended Technique
1. Discover the AI assistant endpoint.
2. Establish normal assistant behaviour.
3. Identify that user input is incorporated directly into the assistant context.
4. Construct a prompt injection that attempts to override the previous instructions.
5. Extract the hidden system context or protected internal record.
6. Recover the ADV-02 flag.

## Flag
CITS3006{ADV02_PROMPT_INJECTION}
