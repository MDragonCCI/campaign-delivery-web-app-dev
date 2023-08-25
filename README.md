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
    - 8.1 [Data Handling](#81-data-handling)
    - 8.2 [Authorization and Authentication](#82-authorization-and-authentication)
9. [Maintenance and Updates](#9-maintenance-and-updates)
    - 9.1 [Regular Maintenance](#91-regular-maintenance)
    - 9.2 [Updates and Versioning](#92-updates-and-versioning)
10. [Appendix](#10-appendix)
    - 10.1 [Glossary](#101-glossary)
    - 10.2 [Resources](#102-resources)
    - 10.3 [Contact Information](#103-contact-information)

---

## 1. Introduction

### 1.1 Purpose

The Campaign Extractor is a software tool designed to extract relevant data from broadsign control domains to help with montioring campaign delivery. It simplifies the process of gathering campaign-related information from the Broadsign Direct API. 

### 1.2 Scope

This document provides technical information about the Campaign Extractor, including installation instructions, configuration options, usage guidelines, and advanced features.

### 1.3 Audience

This documentation is intended for system administrators, developers, and technical users who are responsible for setting up, configuring, and using the Campaign Extractor tool.

---

## 2. System Overview

### 2.1 Architecture

The campaign extractor currently works using the following components

- Front-end Server
- Campaign extractor script

### 2.2 Dependencies

The Campaign Extractor relies on the following dependencies:

- Python 3.9
- Jinja2
- Access to the broadsign direct domains where the data is held

---

## 3. Installation and Setup

### 3.1 Prerequisites

- Python 3.9 should be installed.
- Ensure you have the necessary permissions within broadsign direct in order to effectively access the information. 

### 3.2 Installation Steps

1. Clone the Campaign Extractor repository from [GitHub Repo URL].
2. Navigate to the extracted directory.
3. Create a virtual environment (recommended) using `python3 -m venv venv` and activate it.
4. Install required packages using `pip install -r requirements.txt`.
5. Configure the tool as described in the next section.

---

## 4. Configuration

### 4.1 Configuration File

The configuration file (`app_config.py`) contains settings for connecting the script to the azure fuction.

### 4.2 Parameters

- `data_sources`: List of data sources with connection details.
- `extraction_rules`: Rules specifying how to extract campaign data from each data source.
- `output_format`: Desired format for the extracted data (e.g., JSON, CSV).
- Additional parameters specific to data source connectors and output formatters.

---

## 5. Usage

### 5.1 Command Line Interface

Run the Campaign Extractor using the following command:

```bash
python campaign_extractor.py --config config.yaml
