import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Hero from './components/Hero'
import Navbar from './components/Navbar'
import About from './components/About'
import Technology from './components/Technology'
import Team from './components/Team'
import FutureVision from './components/FutureVision'
import SplashCursor from '../Reactbits/SplashCursor/SplashCursor'
import Implementation from './components/Implementation'
import ButtonImplementation from './components/ButtonImplementation'
import LiveCamera from './components/LiveCamera'   // 👈 NEW

const MainLayout = () => (
  <div className='font-sans max-w-screen-lg mx-auto'>
    <Navbar />
    <Hero />
    <About />
    <Technology />
    <Team />
    <Implementation />
    <FutureVision />
  </div>
)

const App = () => {
  return (
    <Router>
      <SplashCursor />
      <Routes>
        <Route path="/" element={<MainLayout />} />
        <Route path="/upload" element={<ButtonImplementation />} />
        <Route path="/live" element={<LiveCamera />} />   {/* 👈 NEW */}
      </Routes>
    </Router>
  )
}

export default App
