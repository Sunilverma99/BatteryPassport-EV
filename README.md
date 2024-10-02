# Battery Passport Smart Contract for Electric Vehicles

## Overview

This smart contract implements a battery passport system for electric vehicle batteries, compliant with EU regulations. It uses blockchain technology to track the lifecycle of batteries from manufacture to recycling, storing crucial data about each battery's characteristics, performance, and sustainability metrics.

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
2. `viewBatteryDetails`: Allows consumers to view battery information
3. `removeManufacturer`: Allows the government to remove a manufacturer from the system
4. `removeSupplier`: Allows the government to remove a supplier from the system
5. `removeConsumer`: Allows the government to revoke the consumer role from an address
6. `removeRecycler`: Allows the government to remove a recycler from the system

## Data Update Responsibilities

Different entities are responsible for updating specific fields in the BatteryData struct:

### Manufacturer
- batteryModel
- manufacturerLocation
- batteryType
- productName

### Consumer
- Can view battery details (batteryType, batteryModel, productName, manufacturingSite)
- Can report issues with the battery

### Recycler
- Can indicate that a battery has been received for recycling
- Can mark a battery as recycled
- Can return recycled materials to the manufacturer

### Government
- Manages all roles (add/remove manufacturers, suppliers, consumers, recyclers)

## Usage Flow

1. Government deploys the contract and authorizes manufacturers, suppliers, and recyclers
2. Manufacturer creates a new battery entry, providing initial data
3. Consumer can view battery information and report any issues
4. Recycler receives the battery, marks it as recycled, and can indicate return of materials to the manufacturer
5. Government oversees the process and can remove stakeholders if necessary

## Data Privacy and Access Control

- Implements role-based access control to ensure only authorized entities can modify specific data fields
- `viewBatteryDetails` function is restricted to users with the CONSUMER_ROLE

## Compliance and Verification

- The contract structure allows for storing key information required by EU regulations
- Government role enables oversight and management of stakeholders

## Future Enhancements

- Implement functions for suppliers to update supply chain information
- Expand the BatteryData struct to include more detailed information as required by EU regulations
- Implement a more sophisticated mechanism for consumers to report issues
- Add functions to update battery health, performance, and durability over time
- Develop a system for tracking recycled materials returned to manufacturers

This smart contract provides a foundation for a comprehensive battery passport system, enabling transparent tracking of electric vehicle batteries throughout their lifecycle, from production to recycling and potential reuse of materials.