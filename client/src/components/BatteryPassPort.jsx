import React from 'react'
import { Battery, Truck, Factory, Recycle, AlertTriangle, Award, Activity, Settings, Dice1 } from 'lucide-react'

export default function Component() {
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
      <div className='w-full bg-gradient-to-br from-gray-900 via-black to-gray-900 pt-2'>
         <div className="bg-white from-gray-900 via-black to-gray-900 p-6 max-w-2xl mx-auto shadow-lg rounded-lg">
      <div className="mb-6">
        <div className="flex items-center mb-2">
          <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
          <h1 className="text-2xl font-bold">EV BATTERY</h1>
        </div>
        <h2 className="text-3xl font-bold">
          <span className="text-red-500">Marklytics</span> Battery Passport
        </h2>
      </div>

      <div className="mb-6">
        <p className="text-lg"><span className="font-semibold">Battery ID:</span> {batteryData.id}</p>
        <div className="flex items-center mt-2">
          <Battery className="w-6 h-6 mr-2" />
          <span className="bg-gray-200 px-3 py-1 rounded-full">{batteryData.weight}</span>
        </div>
        <div className="flex items-center mt-2">
          <Truck className="w-6 h-6 mr-2" />
          <span className="bg-gray-200 px-3 py-1 rounded-full">Batch Traceability</span>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Required Information</h3>
        <div className="grid grid-cols-2 gap-4">
          {batteryData.requiredInfo.map((info, index) => (
            <div key={index} className="flex items-center">
              <info.icon className="w-6 h-6 mr-2" />
              <div>
                <p className="text-sm text-gray-600">{info.label}</p>
                <p className="font-semibold">{info.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Additional Information</h3>
        <div className="grid grid-cols-2 gap-4">
          {batteryData.additionalInfo.map((info, index) => (
            <div key={index} className="flex items-center">
              <info.icon className="w-6 h-6 mr-2" />
              <div>
                <p className="text-sm text-gray-600">{info.label}</p>
                <p className="font-semibold">{info.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-3">Chain of Custody</h3>
        <div className="relative pl-8">
          <Truck className="absolute left-0 top-0 w-6 h-6 text-gray-600" />
          <div className="border-l-2 border-gray-300 pl-6 pb-6">
            {batteryData.chainOfCustody.map((event, index) => (
              <div key={index} className="mb-4 relative">
                <div className="absolute -left-8 top-1 w-4 h-4 bg-white border-2 border-gray-300 rounded-full"></div>
                <p className="text-sm text-gray-600">{event.date}</p>
                <p className="font-semibold">{event.event}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 text-right text-sm text-gray-500">
        Digital Product passport by Marklytics
      </div>
    </div>
      </div>
  )
}