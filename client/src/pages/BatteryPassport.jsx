import React from 'react'
import BatteryPassPortComponent from '../components/BatteryPassPortComponent'
import { Battery, Truck, Factory, Recycle, AlertTriangle, Award, Activity, Settings, Dice1 } from 'lucide-react'
import { useParams } from 'react-router-dom'

function BatteryPassport() {
    const batteryData = {
        id: '0Xf4r...G937',
        weight: '175 kg',
        requiredInfo: [
          { icon: Battery, label: 'Battery Type', value: 'Lithium-Ion' },
          { icon: Activity, label: 'Durability', value: '8 years / 160,000 km' },
          { icon: Settings, label: 'Battery Model', value: 'EV75-85' },
          { icon: Activity, label: 'Performance', value: '75 kWh' },
        ],
        additionalInfo: [
          { icon: Battery, label: 'Product Name', value: 'EcoPower 75' },
          { icon: Factory, label: 'GHG Emissions', value: '6.5 tCO2e' },
          { icon: Factory, label: 'Manufacturing Site', value: 'Gigafactory 1, Nevada' },
          { icon: Award, label: 'Declaration of Conformity', value: 'EU 2006/66/EC' },
          { icon: Recycle, label: 'Recycled Content', value: '12% by weight' },
          { icon: AlertTriangle, label: 'Hazardous Substance', value: 'See detailed report' },
          { icon: Recycle, label: 'End of Life Collection Information', value: 'Available' },
          { icon: Award, label: 'Certifications', value: 'ISO 14001, IATF 16949' },
          { icon: Activity, label: 'Battery Health', value: '98%' },
          { icon: Truck, label: 'Supply Chain due Diligence Policy', value: 'Implemented' },
        ],
        chainOfCustody: [
          { date: '08/07/2023, 11:00', event: 'Battery Serviced' },
          { date: '12/09/2021, 08:00', event: 'Car sold to Consumer' },
          { date: '27/08/2021, 19:30', event: 'Battery Serviced' },
          { date: '14/07/2021, 11:00', event: 'Battery Sold to automotive OEM' },
        ],
      }
  return (
    <BatteryPassPortComponent batteryData={batteryData} />
  )
}

export default BatteryPassport