
import { 
  Smartphone, 
  Globe, 
  Zap, 
  ShieldCheck, 
  BarChart, 
  Users 
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const servicesData = [
  {
    icon: <Smartphone className="h-8 w-8 text-dnnr-teal" />,
    title: "Mobile App Development",
    description: "Native and cross-platform applications powered by AI to deliver personalized user experiences."
  },
  {
    icon: <Globe className="h-8 w-8 text-dnnr-teal" />,
    title: "Web Development",
    description: "Responsive, intelligent web applications and platforms that adapt to user behavior."
  },
  {
    icon: <Zap className="h-8 w-8 text-dnnr-teal" />,
    title: "AI Integration",
    description: "Seamlessly integrate cutting-edge AI technologies to make your applications smarter."
  },
  {
    icon: <ShieldCheck className="h-8 w-8 text-dnnr-teal" />,
    title: "Secure Solutions",
    description: "Enterprise-grade security ensuring your data and user information are protected."
  },
  {
    icon: <BarChart className="h-8 w-8 text-dnnr-teal" />,
    title: "Analytics Integration",
    description: "Data-driven insights to better understand your users and optimize your applications."
  },
  {
    icon: <Users className="h-8 w-8 text-dnnr-teal" />,
    title: "User-Centric Design",
    description: "Beautiful, intuitive interfaces that put your users' needs first."
  }
];

const Services = () => {
  return (
    <section id="services" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-dnnr-blue mb-4">
            Our <span className="text-dnnr-teal">Services</span>
          </h2>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto">
            We specialize in building intelligent digital solutions that transform how people interact with technology.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {servicesData.map((service, index) => (
            <Card key={index} className="border border-gray-200 transition-all hover:shadow-md hover:border-dnnr-teal/20">
              <CardHeader className="pb-2">
                <div className="mb-4">{service.icon}</div>
                <CardTitle className="text-xl font-bold text-dnnr-blue">{service.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-700">{service.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
