import React from 'react'
import { Link } from 'react-router-dom'

const Hero = () => {
  return (
    <section className="relative min-h-[100dvh] h-screen w-full flex items-center justify-center overflow-hidden">
      <div className="max-w-screen-lg mx-auto px-6 md:px-8 py-16 flex flex-col justify-center items-center text-center gap-6 z-10">
        <p className="text-[1.2rem] md:text-[1.5rem] text-[#64dfdf] font-semibold leading-tight">
          Give Voice to the Voiceless
        </p>
        <h1 className="text-3xl md:text-5xl font-bold animate-fadeIn text-[#56cfe1]">
          Silent Speech Recognition <br /> for the Voiceless
        </h1>
        <p className="text-base md:text-xl text-[#64dfdf] max-w-4xl">
          Welcome to Silent Speech Recognition, a revolutionary approach to communication for those who cannot speak. Our technology enables individuals to express themselves through silent gestures and movements, bridging the gap between thought and speech.
        </p>

       
        <p className="mt-4 text-[1.5rem] font-bold text-[#64dfdf]">
          Get Started with Silent Speech Recognition Today!
        </p>
        <div className="flex gap-4 mt-4">
          <Link
            to="/upload"
            className="px-6 py-3 w-40 text-center md:text-[1.1rem] bg-[#64dfdf] text-black rounded-full text-lg font-medium hover:bg-[#a0fcfc] transition"
          >
            Upload Video
          </Link>
          <Link
            to="/live"
            className="px-6 py-3 w-40 text-center md:text-[1.1rem] bg-[#64dfdf] text-black rounded-full text-lg font-medium hover:bg-[#a0fcfc] transition"
          >
            Live
          </Link>
        </div>
      </div>
    </section>
  )
}

export default Hero
