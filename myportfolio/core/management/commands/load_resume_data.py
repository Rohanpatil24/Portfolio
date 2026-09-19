from django.core.management.base import BaseCommand
from core.models import PersonalInfo, Experience, Project, Skill, Education

class Command(BaseCommand):
    help = "Loads Rohan's resume data into the database"

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old data...")
        PersonalInfo.objects.all().delete()
        Experience.objects.all().delete()
        Project.objects.all().delete()
        Skill.objects.all().delete()
        Education.objects.all().delete()

        self.stdout.write("Adding Personal Info...")
        PersonalInfo.objects.create(
            name="Rohan Patil",
            tagline="Results-driven Software Developer",
            about_text="Results-driven Software Developer with 2 years of experience in designing and implementing scalable web applications. Skilled in Full Stack Development with a strong focus on backend technologies, including Django REST Framework, MySQL, and Redis caching for high-performance APIs. Proven ability to integrate third-party services, optimize system performance, and deliver secure, efficient solutions. Adept at collaborating in agile environments, quickly mastering new technologies, and contributing to end-to-end project development. Passionate about building robust applications that enhance business processes and user experience.",
            email="rohanrpatil24@gmail.com",
            phone="+91 9653639991",
            location="Mumbai, Maharashtra",
            linkedin_url="https://linkedin.com/",
            github_url="https://github.com/Rohanpatil24"
        )

        self.stdout.write("Adding Experience...")
        Experience.objects.create(
            role="Junior Software Developer",
            company="Antariksh Softtech Private Limited",
            duration="October 2024 - Current",
            description="• Designing and building robust web applications using Django, RESTful APIs, MySQL databases, and modern frontend technologies like Tailwind CSS.\n• Managing full project lifecycles including backend development, database optimization, API integrations, authentication systems, and production deployments on Windows IIS.\n• Designing, Debugging complex issues, implementing secure user authentication, creating responsive UIs with smooth animations, and ensuring scalable, production-ready code quality.",
            order=1
        )
        Experience.objects.create(
            role="Network Engineer L1",
            company="Antariksh Softtech Private Limited",
            duration="July 2023 - October 2024",
            description="• Maintaining and administering computer networks and related computing environments including systems software, applications software, hardware, and configurations.\n• Protecting data, software, and hardware by coordinating, planning, and implementing network security measures, Maintaining, configuring, and monitoring.\n• Designing, configuring, and testing networking software, computer hardware, and operating system software.",
            order=2
        )
        Experience.objects.create(
            role="Material Officer",
            company="Reliance Digital Retail LTD",
            duration="September 2021 - January 2023",
            description="• Inventory Management, SAP Handling.\n• Data analysis, Inward & Outward, Verbal and written communication, Advance Excel, Power Point and Word.\n• Directs production and inventory control, shipping and receiving, and materials storage, Directs production planning and scheduling based on sales forecasts.",
            order=3
        )
        Experience.objects.create(
            role="Cashier",
            company="Big Bazaar (Future Group)",
            duration="September 2018 - January 2021",
            description="• Manage transactions with customers using cash registers, Cross-sell products and introduce new ones and Scan goods and ensure pricing is accurate.\n• Collect payments whether in cash or credit, Issue receipts, refunds, change or tickets.",
            order=4
        )

        self.stdout.write("Adding Projects...")
        projects_data = [
            ("Productivity Portal", "Dec 2025", "Django Rest framework API, MySQL Workbench", "Developed and maintained the Productivity Portal, a system that tracks daily activities of staff and generates detailed daily, weekly, and monthly reports. The portal integrates with third-party tools such as HRMS (Height8) for automation and Microsoft Teams for meeting scheduling. Implemented Redis caching to ensure faster data processing. Calculates monthly incentives and includes an internal ticketing system.", "ph-folder", 1),
            ("New Connection Portal", "Oct 2024", "Django Rest framework API, MYSQL Workbench", "Developed a landing page for new I-ON customers to register with OTP verification. Supports a referral system that calculates monthly incentives for employees. Optimized API performance and scalability by integrating Redis caching.", "ph-folder", 2),
            ("Banquet Booking and Event Celebration", "April 2024", "HTML, CSS, BootStrap, Django, JavaScript", "Website where customers can book the Banquet and select the Menu for their Event. User can Pay the full amount or pay the booking amount. Login and registration integrated for users with Razorpay payment gateway.", "ph-folder", 3),
            ("Ecart", "March 2024", "HTML, CSS, BootStrap, Django", "Ecommerce Project where customers or users can buy electronics, clothes, etc. Login and registration integrated along with Razorpay gateway. UI is designed with Bootstrap.", "ph-shopping-cart", 4),
            ("Message App", "Feb 2024 - Mar 2024", "Django, MySQL", "Web App created with Django. New Users need to create an account, Existing users can create a group and Chat together. Message contains text and datetime module for live current data.", "ph-chat-circle", 5),
            ("Nike Catalogues Website", "Feb 2024", "HTML, CSS, JavaScript", "Website containing a Home Page, Get in Touch Page, and Product Details Page. Features CSS 3D Transformations and Animation for an awesome interface.", "ph-sneaker", 6),
            ("MyTodoList", "Feb 2023 - Mar 2023", "React", "User can create and delete Todos on the Web.", "ph-list-checks", 7),
            ("ConnectFour App", "Mar 2023 - Apr 2023", "Core Java", "Traditional board Game created with Java Language using Intellij IDEA Software. Requires two users and features a Graphical user Interface.", "ph-game-controller", 8),
        ]
        
        for title, _, tech_stack, desc, icon, order in projects_data:
            Project.objects.create(title=title, description=desc, tech_stack=tech_stack, icon_class=icon, order=order)

        self.stdout.write("Adding Skills...")
        backend = ['Django', 'MySQL', 'SQL Server', 'Python', 'Core Java', 'RESTful APIs', 'Redis']
        frontend = ['HTML', 'Bootstrap', 'CSS', 'JavaScript', 'Tailwind CSS', 'React']
        tools = ['AWS', 'GitHub', 'Networking', 'Microsoft Office', 'Photoshop CS6']

        for skill in backend:
            Skill.objects.create(name=skill, category='backend')
        for skill in frontend:
            Skill.objects.create(name=skill, category='frontend')
        for skill in tools:
            Skill.objects.create(name=skill, category='tools')

        self.stdout.write("Adding Education & Certifications...")
        education_data = [
            ("Master in Full Stack Web Development With AWS", "IT-Vedant, Thane", "December 2023", False),
            ("Bachelor's Degree in Computer Science", "Model College of Science And Commerce, Dombivali", "April 2021", False),
            ("Maharashtra State Board of HSC", "K.D.College of Science, Arts And Commerce, Vittalwadi", "February 2018", False),
            ("Maharashtra State Board of SSC", "R.B.T.Vidayalaya, Dombivali", "March 2016", False),
        ]
        
        cert_data = [
            ("Python for Web Development", "IBM", "21/05/2024"),
            ("Programming Foundation & SQL", "IT-Vedant", "16/05/2024"),
            ("Web Designing Basics", "IT-Vedant", "16/05/2024"),
            ("Advance SQL & MongoDB", "IT-Vedant", "14/05/2024"),
            ("Advance Web Designing", "IT-Vedant", "30/03/2024"),
            ("Web Developer", "Internshala.com", "02/20/2023"),
            ("AWS (Amazon Web Services)", "Internshala.com", "03/17/2023"),
            ("Core Java", "Internshala.com", "03/03/2023"),
            ("Support Star of the Month", "Reliance Digital Retail LTD", "06/10/22 & 02/06/22")
        ]

        for title, inst, date, is_cert in education_data:
            Education.objects.create(title=title, institution=inst, date_completed=date, is_certification=is_cert)
            
        for title, inst, date in cert_data:
            Education.objects.create(title=title, institution=inst, date_completed=date, is_certification=True)

        self.stdout.write(self.style.SUCCESS("Successfully loaded Rohan's portfolio data!"))