import React from "react"
import { Link } from "react-router-dom"

const Navbar = () => {
  return (
    <header className="w-full bg-white shadow-md fixed top-0 left-0 z-50">
      <div className="max-w-screen-lg mx-auto px-6 md:px-8 py-4 flex items-center justify-between">
        {/* Logo / Brand */}
        <Link
          to="/"
          className="text-xl md:text-2xl font-bold text-primary-dark hover:text-primary transition-colors"
        >
          SilentSpeech
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex gap-6 text-primary-dark font-medium">
          <a href="#about" className="hover:text-primary transition-colors">About</a>
          <a href="#technology" className="hover:text-primary transition-colors">Technology</a>
          <a href="#team" className="hover:text-primary transition-colors">Team</a>
          <a href="#contact" className="hover:text-primary transition-colors">Contact</a>

          {/* Route-based links */}
          <Link to="/upload" className="hover:text-primary transition-colors">Upload</Link>
          <Link to="/live" className="hover:text-primary transition-colors">Live</Link>
        </nav>

        {/* Mobile Menu Icon */}
        <button className="md:hidden text-primary-dark focus:outline-none">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
      </div>
    </header>
  )
}

export default Navbar
