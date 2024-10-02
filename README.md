# Battery Passport Smart Contract for Electric Vehicles

## Overview

This smart contract implements a battery passport system for electric vehicle batteries, compliant with EU regulations. It uses blockchain technology to track the lifecycle of batteries from manufacture to recycling, storing crucial data about each battery's characteristics, performance, and sustainability metrics. The contract now includes a consent mechanism to ensure data privacy and user control.

## Contract Logic

### Roles

1. Government
2. Manufacturer
3. Supplier
4. Consumer
5. Recycler

### Main Data Structure

The contract uses a `BatteryData` struct to store the following information:

- `Identification`:
  - `batteryModel`: Identifier for the battery model
  - `manufacturerLocation`: Location where the battery was manufactured
- `TechnicalSpecifications`:
  - `batteryType`: Type of the battery
- `productName`: Name of the product containing the battery

### Key Functions

1. `setBatteryData`: Called by authorized manufacturers to create a new battery entry and mint an associated token
2. `viewBatteryDetails`: Allows consumers to view battery information (requires consent)
3. `removeManufacturer`: Allows the government to remove a manufacturer from the system
4. `removeSupplier`: Allows the government to remove a supplier from the system
5. `removeConsumer`: Allows the government to revoke the consumer role from an address
6. `removeRecycler`: Allows the government to remove a recycler from the system
7. `giveConsent`: Allows battery owners to give consent for their battery data to be viewed
8. `revokeConsent`: Allows battery owners to revoke consent for their battery data to be viewed

## Data Privacy and Access Control

- Implements role-based access control to ensure only authorized entities can modify specific data fields
- `viewBatteryDetails` function is restricted to users with the CONSUMER_ROLE and requires consent from the battery owner
- Consent mechanism allows battery owners to control access to their battery's data

## Usage Flow

1. Government deploys the contract and authorizes manufacturers, suppliers, and recyclers
2. Manufacturer creates a new battery entry, providing initial data
3. Battery owner gives consent for their battery data to be viewed
4. Consumer can view battery information (if consent is given) and report any issues
5. Battery owner can revoke consent at any time
6. Recycler receives the battery, marks it as recycled, and can indicate return of materials to the manufacturer
7. Government oversees the process and can remove stakeholders if necessary

The addition of the consent function enhances data privacy and gives battery owners more control over their information, aligning with data protection regulations and best practices.

