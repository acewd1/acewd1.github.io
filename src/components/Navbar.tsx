
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Menu, X } from "lucide-react";

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="bg-white/95 sticky top-0 z-50 backdrop-blur-sm border-b border-gray-100">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center">
          <a href="/" className="text-2xl font-bold text-dnnr-blue">
            DNNR<span className="text-dnnr-teal">Tech</span>
          </a>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          <a href="#services" className="text-gray-700 hover:text-dnnr-blue transition-colors">
            Services
          </a>
          <a href="#benefits" className="text-gray-700 hover:text-dnnr-blue transition-colors">
            Benefits
          </a>
          <a href="#technology" className="text-gray-700 hover:text-dnnr-blue transition-colors">
            Technology
          </a>
          <a href="#contact" className="text-gray-700 hover:text-dnnr-blue transition-colors">
            Contact
          </a>
          <Button className="bg-dnnr-teal hover:bg-dnnr-teal/90">Get Started</Button>
        </div>

        {/* Mobile Navigation Toggle */}
        <div className="md:hidden">
          <button onClick={toggleMenu} aria-label="Toggle Menu" className="text-gray-700 p-2">
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 py-4 px-4">
          <div className="flex flex-col space-y-4">
            <a href="#services" className="text-gray-700 hover:text-dnnr-blue py-2" onClick={toggleMenu}>
              Services
            </a>
            <a href="#benefits" className="text-gray-700 hover:text-dnnr-blue py-2" onClick={toggleMenu}>
              Benefits
            </a>
            <a href="#technology" className="text-gray-700 hover:text-dnnr-blue py-2" onClick={toggleMenu}>
              Technology
            </a>
            <a href="#contact" className="text-gray-700 hover:text-dnnr-blue py-2" onClick={toggleMenu}>
              Contact
            </a>
            <Button className="bg-dnnr-teal hover:bg-dnnr-teal/90 w-full">Get Started</Button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
