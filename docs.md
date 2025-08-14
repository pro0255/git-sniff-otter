# Git Inspector LLM Report Generator

## 1. Introduction

The objective of this project is to create an automated reporting tool that analyzes a specified set of local Git repositories within a defined time window. It will utilize the `gitinspector` tool to gather repository statistics, combine this data with detailed commit information, and then use a Large Language Model (LLM) to generate a comprehensive, human-readable report. This report will be automatically delivered to a designated Slack channel.

## 2. Functional Requirements

This section details the specific features and behaviors the system must exhibit.

### 2.1. Data Input & Configuration

* **FR-1:** The system shall accept a list of local file paths, each pointing to a Git repository.
* **FR-2:** The system shall require the user to be authenticated with Git locally to access the repositories.
* **FR-3:** The system shall allow the user to specify a time window (e.g., "last week," "last month," or a specific date range) for the analysis.
* **FR-4:** The system shall be configurable with an API key or token for accessing the LLM service.
* **FR-5:** The system shall be configurable with a Slack webhook URL or API token and a target channel for report delivery.

### 2.2. Data Processing

* **FR-6:** For each repository path provided, the system shall execute `gitinspector` to gather statistics (e.g., lines of code, commits per author).
* **FR-7:** The system shall programmatically retrieve the commit history for each repository within the specified time window.
* **FR-8:** The system shall merge the `gitinspector` data with the individual commit data to create a structured dataset for each repository and each author.

### 2.3. LLM Report Generation

* **FR-9:** The system shall use an LLM to generate a single, coherent report based on the processed data.
* **FR-10:** The report shall include an overall summary of activity in the repository for the given time window.
* **FR-11:** The report shall contain a section with repository-wide statistics.
* **FR-12:** The report shall contain a section for each engineer, describing their individual contributions and key statistics (e.g., number of commits, files changed, lines added/removed).

### 2.4. Output & Delivery

* **FR-13:** The system shall deliver the final LLM-generated report to the configured Slack channel.

## 3. Non-Functional Requirements

This section describes the qualities and constraints of the system.

* **NFR-1:** **Performance:** The data processing and report generation should be completed within a reasonable timeframe (e.g., less than 5 minutes for 10 repositories).
* **NFR-2:** **Security:** The system shall handle API keys and tokens securely, avoiding hardcoding them in the source code.
* **NFR-3:** **Maintainability:** The codebase should be well-documented and modular to allow for easy updates to the LLM or output destinations.
* **NFR-4:** **Usability:** The configuration process (e.g., setting paths and tokens) should be straightforward and well-documented.

## 4. Assumptions & Constraints

* **A-1:** The `gitinspector` tool is assumed to be pre-installed and available in the execution environment's path.
* **A-2:** The system will be executed in an environment with local file system access to the target repositories.
* **C-1:** The system's execution is limited to a local machine; it will not be deployed as a web service.
* **C-2:** The LLM's response format is assumed to be consistent and can be reliably parsed for inclusion in the final report.

## 5. High-Level Architecture

The system can be visualized as a linear pipeline:

1.  **Input Module:** Accepts repository paths, time window, and API credentials.
2.  **Data Collection Module:** Calls `gitinspector` and Git CLI commands to collect raw data.
3.  **Data Transformation Module:** Parses and structures the raw data into a format suitable for the LLM.
4.  **LLM Integration Module:** Sends the structured data to the LLM and receives the generated report.
5.  **Output Module:** Uses the Slack API to format and send the report to the target channel.