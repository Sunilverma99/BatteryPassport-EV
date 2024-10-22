import React from 'react'
import { Battery, Truck } from 'lucide-react'

export default function Component({ batteryData }) {
  return (
      <div className='w-full bg-gradient-to-br from-gray-900 via-black to-gray-900 pt-2'>
         <div className="bg-white from-gray-900 via-black to-gray-900 p-6  mx-auto shadow-lg rounded-lg">
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