
import React from 'react'
import { motion } from 'framer-motion'
import { Battery, Shield, Recycle, Users, Building2, Zap, ChevronRight, Truck, User, Lock, Database, Wallet } from 'lucide-react'

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
}

export default function Component() {
  const features = [
    { icon: Shield, title: "Data Privacy & Consent", description: "Secure control over battery data access with advanced encryption", color: "from-blue-400 to-blue-600" },
    { icon: Database, title: "Blockchain Tracking", description: "Immutable lifecycle tracking from production to recycling", color: "from-purple-400 to-purple-600" },
    { icon: Lock, title: "Role-Based Access", description: "Tailored permissions for all stakeholders in the ecosystem", color: "from-indigo-400 to-indigo-600" },
  ]

  const roles = [
    { icon: Building2, title: "Government", description: "Oversees the system, authorizes roles, and ensures compliance with regulations.", color: "from-purple-500 to-indigo-600" },
    { icon: Battery, title: "Manufacturer", description: "Registers batteries and provides technical specifications to the system.", color: "from-green-500 to-emerald-600" },
    { icon: Truck, title: "Supplier", description: "Manages battery distribution and updates delivery statuses.", color: "from-yellow-500 to-amber-600" },
    { icon: User, title: "Consumer", description: "Views battery information and gives/revokes consent for data access.", color: "from-red-500 to-rose-600" },
    { icon: Recycle, title: "Recycler", description: "Updates the system when a battery is recycled and provides details on material recovery.", color: "from-blue-500 to-cyan-600" },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-black/30 backdrop-blur-lg border-b border-gray-500/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-2xl flex gap-3 font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            <img className='w-8 h-6' src="Logo.png" alt="" />
            <img className='w-full h-6' src="LogoName.png" alt="" />
          </div>
          <button className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full hover:from-blue-600 hover:to-purple-700 transition duration-300 flex items-center space-x-2 shadow-lg hover:shadow-blue-500/25">
            <Wallet className="h-5 w-5" />
            <span>Connect Wallet</span>
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div {...fadeIn} className="text-center">
            <h2 className="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
              Battery Passport for Electric Vehicles
            </h2>
            <p className="text-xl mb-10 max-w-2xl mx-auto text-gray-300">
              Revolutionizing EV battery lifecycle management with blockchain technology
            </p>
            <button className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full hover:from-blue-700 hover:to-purple-700 transition duration-300 shadow-lg hover:shadow-purple-500/25">
              Learn More
            </button>
          </motion.div>
        </div>
      </section>

      {/* Enhanced Key Features Section */}
      <section className="py-20 bg-gray-900/50 backdrop-blur-lg">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            Key Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                {...fadeIn}
                transition={{ delay: index * 0.1 }}
                className={`bg-gradient-to-br ${feature.color} rounded-lg p-1 hover:shadow-lg hover:shadow-${feature.color.split('-')[1]}-500/20 transition-all duration-300 group`}
              >
                <div className="bg-gray-900 p-6 rounded-lg h-full flex flex-col items-center text-center">
                  <feature.icon className="h-16 w-16 mb-4 text-gray-300 group-hover:text-white transition-colors duration-300" />
                  <h3 className="text-xl font-bold mb-2 text-gray-300 group-hover:text-white transition-colors duration-300">{feature.title}</h3>
                  <p className="text-gray-400 group-hover:text-gray-200 transition-colors duration-300">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            Roles in the System
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {roles.map((role, index) => (
              <motion.div
                key={index}
                {...fadeIn}
                transition={{ delay: index * 0.1 }}
                className={`bg-gradient-to-br ${role.color} p-1 rounded-lg hover:shadow-lg hover:shadow-${role.color.split('-')[1]}-500/20 transition-all duration-300 group`}
              >
                <div className="bg-gray-900 p-6 rounded-lg h-full flex flex-col">
                  <div className="flex items-center mb-4">
                    <role.icon className="h-8 w-8 text-gray-300 group-hover:text-white transition-colors duration-300" />
                    <h3 className="text-xl font-bold ml-3 text-gray-300 group-hover:text-white transition-colors duration-300">{role.title}</h3>
                  </div>
                  <p className="text-gray-400 group-hover:text-gray-200 transition-colors duration-300 flex-grow">{role.description}</p>
                  <div className="mt-4 flex justify-end">
                    <button className="text-sm text-gray-400 hover:text-white transition-colors duration-300 flex items-center">
                      Learn more <ChevronRight className="ml-1 h-4 w-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-900/50 backdrop-blur-lg">
        <div className="container mx-auto px-4 text-center">
          <motion.div {...fadeIn}>
            <h2 className="text-4xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
              Ready to Get Started?
            </h2>
            <p className="text-xl mb-10 max-w-2xl mx-auto text-gray-300">
              Join the revolution in EV battery management and contribute to a sustainable future.
            </p>
            <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full text-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition duration-300 flex items-center mx-auto shadow-lg hover:shadow-purple-500/25">
              Join Now <Zap className="ml-2 h-5 w-5" />
            </button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black/70 py-6 border-t border-gray-500/20">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-gray-400">© 2024 Battery Passport. All Rights Reserved.</p>
        </div>
      </footer>
    </div>
  )
}