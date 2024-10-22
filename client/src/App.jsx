import React from 'react'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from './pages/Home'
import Header from './pages/Header'
import Footer from './pages/Footer'
import BatteryPassport from './pages/BatteryPassport'


export default function App() {
  return (
    <div>
      <Header />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/battery-passport/:id" element={<BatteryPassport />} />
        </Routes>
      </BrowserRouter>
      <Footer />

    </div>
  )
}
