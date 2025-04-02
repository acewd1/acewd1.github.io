
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Mail, Phone, MapPin } from "lucide-react";

const Contact = () => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Form submission logic would go here
    console.log("Form submitted");
  };

  return (
    <section id="contact" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-dnnr-blue mb-4">
            Get <span className="text-dnnr-teal">In Touch</span>
          </h2>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto">
            Have a project in mind? Contact us to discuss how our AI-powered solutions can help your business grow.
          </p>
        </div>

        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="bg-white rounded-2xl shadow-md p-8">
            <h3 className="text-2xl font-bold text-dnnr-blue mb-6">Send Us a Message</h3>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="name" className="block mb-2 text-sm font-medium text-gray-700">
                  Your Name
                </label>
                <Input 
                  id="name" 
                  placeholder="Enter your name" 
                  className="w-full border-gray-300"
                />
              </div>
              
              <div>
                <label htmlFor="email" className="block mb-2 text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <Input 
                  id="email" 
                  type="email" 
                  placeholder="Enter your email" 
                  className="w-full border-gray-300"
                />
              </div>
              
              <div>
                <label htmlFor="message" className="block mb-2 text-sm font-medium text-gray-700">
                  Message
                </label>
                <Textarea 
                  id="message" 
                  placeholder="How can we help you?" 
                  className="w-full border-gray-300 min-h-[120px]"
                />
              </div>
              
              <Button type="submit" className="w-full bg-dnnr-teal hover:bg-dnnr-teal/90">
                Send Message
              </Button>
            </form>
          </div>
          
          <div className="flex flex-col justify-between">
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-dnnr-blue mb-6">Contact Information</h3>
              
              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="mr-4 bg-dnnr-blue/10 p-2 rounded-lg">
                    <Mail className="h-6 w-6 text-dnnr-blue" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-1">Email</h4>
                    <p className="text-gray-700">contact@dnnrtech.com</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="mr-4 bg-dnnr-teal/10 p-2 rounded-lg">
                    <Phone className="h-6 w-6 text-dnnr-teal" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-1">Phone</h4>
                    <p className="text-gray-700">+1 (555) 123-4567</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="mr-4 bg-dnnr-blue/10 p-2 rounded-lg">
                    <MapPin className="h-6 w-6 text-dnnr-blue" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-1">Location</h4>
                    <p className="text-gray-700">123 Tech Avenue, San Francisco, CA 94107</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-100 p-6 rounded-xl">
              <h4 className="font-bold text-dnnr-blue mb-2">Office Hours</h4>
              <p className="text-gray-700 mb-4">Monday - Friday: 9:00 AM - 6:00 PM</p>
              <p className="text-gray-500 text-sm">
                We strive to respond to all inquiries within 24 hours during business days.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
