# Campaign Extractor Web App Technical Documentation

## Table of Contents

1. [Introduction](#1-introduction)
    - 1.1 [Purpose](#11-purpose)
    - 1.2 [Scope](#12-scope)
    - 1.3 [Audience](#13-audience)
2. [System Overview](#2-system-overview)
    - 2.1 [Architecture](#21-architecture)
    - 2.2 [Dependencies](#22-dependencies)
3. [Installation and Setup](#3-installation-and-setup)
    - 3.1 [Prerequisites](#31-prerequisites)
    - 3.2 [Installation Steps](#32-installation-steps)
4. [Configuration](#4-configuration)
    - 4.1 [Configuration File](#41-configuration-file)
    - 4.2 [Parameters](#42-parameters)
5. [Usage](#5-usage)
    - 5.1 [Command Line Interface](#51-command-line-interface)
    - 5.2 [Input Specifications](#52-input-specifications)
    - 5.3 [Output Formats](#53-output-formats)
6. [Advanced Features](#6-advanced-features)
    - 6.1 [Data Filtering](#61-data-filtering)
    - 6.2 [Custom Extractor Rules](#62-custom-extractor-rules)
7. [Troubleshooting](#7-troubleshooting)
    - 7.1 [Common Issues](#71-common-issues)
    - 7.2 [Logging](#72-logging)
8. [Security Considerations](#8-security-considerations)
    - 8.1 [Data Handling](#81-data-handling) Saml2.0
    - 8.2 [Authorization and Authentication](#82-authorization-and-authentication)
9. [Maintenance and Updates](#9-maintenance-and-updates)
    - 9.1 [Regular Maintenance](#91-regular-maintenance)
    - 9.2 [Updates and Versioning](#92-updates-and-versioning)
10. [Appendix](#10-appendix)
    - 10.1 [Glossary](#101-glossary)
    - 10.2 [Resources](#102-resources)
    - 10.3 [Contact Information](#103-contact-information) Contact info 

---

## 1. Introduction

### 1.1 Purpose

The Campaign Extractor is a software tool designed to extract relevant data from broadsign control domains to help with montioring campaign delivery. It simplifies the process of gathering campaign-related information from the Broadsign Direct API.

### 1.2 Scope

This document provides technical information about the Campaign Extractor, including installation instructions, configuration options, usage guidelines, and advanced features.

### 1.3 Audience

This documentation is intended for system administrators, developers, and technical users who are responsible for setting up, configuring, and developing the Campaign Extractor tool.

---

## 2. System Overview

### 2.1 Architecture

The campaign extractor currently works using the following components

- **Front-end UI:** This is the place where the user interacts with the script, selecting domains and campaigns
- **Campaign extractor script:** This script compiles data fromt he domain and creates a list of cmapaigns formatted for the planners.
- **Azure App Service:** This is the server hosting for the Campaign extrator app so users can access without needing to download the software.

### 2.2 Dependencies

The Campaign Extractor uses the following dependencies:

- Python 3.9
- Jinja2
- Permission levels for the users on Broadsign Direct Domains.

---

## 3. Installation and Setup

### 3.1 Prerequisites

- Python 3.9 should be installed.
- Ensure you have the necessary permissions within broadsign direct in order to effectively access the information.

### 3.2 Installation Steps

1. Clone the Campaign Extractor repository from [https://github.com/MDragonCCI/campaign-delivery-web-app-dev].
2. Navigate to the extracted directory.
3. Create a virtual environment (recommended) using `python3 -m venv venv` and activate it.
4. Install required packages using `pip install -r requirements.txt`.
5. Configure the tool as described in the next section.

---

## 4. Configuration

### 4.1 Configuration File

The configuration file (`app_config.py`) contains settings for connecting the script to the azure app service.

### 4.2 Parameters

- `Broadsign Domains`: This extractor should work with any Broadsign Direct domains.
- `extraction_rules`: The API will only work with the correct permsission levels for the domain.
- `output_format`: The data can be exported using CSV.
- Additional parameters specific to data source connectors and output formatters.

---

## 5. Usage

### 5.1 Command Line Interface

Run the Campaign Extractor using the following command:

```bash
python app_config.py
```

### 5.2 Input Specifications

- Data sources should be defined in the `data_sources` section of the configuration file.
- Extraction rules in the `extraction_rules` section define how to identify campaign-related data.

### 5.3 Output Formats

The extracted data will be formatted according to the specified `output_format` in the configuration file.

---

## 6. Advanced Features

### 6.1 Data Filtering

Use advanced extraction rules to filter campaign data based on specific criteria, such as date ranges, keywords, or audience segments.

### 6.2 Custom Extractor Rules

Develop custom extractor rules to extract campaign data from data sources with unique structures or APIs.

---

## 7. Troubleshooting

### 7.1 Common Issues

- Verify data source connection details in the configuration file.
- Check for errors in the extraction rules and their compatibility with the data source structure.

### 7.2 Logging

The Campaign Extractor logs its activities to the console and a log file specified in the configuration.

---

## 8. Security Considerations

### 8.1 Data Handling

Ensure that sensitive information such as API keys and passwords are stored securely and not exposed in the configuration.

### 8.2 Authorization and Authentication

Follow best practices for securing access to the data sources, especially when using APIs to extract data.

---

## 9. Maintenance and Updates

### 9.1 Regular Maintenance

Regularly review and update extraction rules as data sources or campaign structures change.

### 9.2 Updates and Versioning

Keep the Campaign Extractor and its dependencies up to date. Use version control for configuration files.

---

## 10. Appendix


### 10.1S Resources

- [https://github.com/MDragonCCI/campaign-delivery-web-app-dev]
- [https://direct.broadsign.com/api/v1/docs/#/]

### 10.3 Contact Information

For support or inquiries, contact [mailto:mytechsupport@clearchannelint.com].

---

*This technical documentation provides a comprehensive guide to setting up, configuring, and using the Campaign Extractor tool. It covers installation, configuration, usage, troubleshooting, security.