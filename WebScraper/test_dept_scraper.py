import os

from rdflib import Graph, Namespace, RDF, Literal, URIRef, XSD, RDFS

from WebScraper.department_scraper import get_page_for_name, get_school_from_page
from WebScraper.swrc import SWRC

name_mappings = {
    "School of Biosystems Engineering": "School of Biosystems and Food Engineering",
    "School of Public Hlth, Physio and Pop Sc": "School of Public Health, Physiotherapy and Sports Science",
    "School of Public Hlth, Phys and Sports Sci": "School of Public Health, Physiotherapy and Sports Science",
    "UCD Institute of Sport and Health": "School of Public Health, Physiotherapy and Sports Science",
    "Woodview House": "School of Public Health, Physiotherapy and Sports Science",
    "School of Architecture, Plan and Env Pol": "School of Architecture, Planning and Environmental Policy",
    "School of Architecture": "School of Architecture, Planning and Environmental Policy",
    "School of Computer Science and Informatics": "School of Computer Science",
    "School of Mechanical and Materials Eng": "School of Mechanical and Materials Engineering",
    "Earth Institute": "UCD Earth Institute",
    "School of Nursing,Midwifery and Health Sys": "School of Nursing, Midwifery & Health Systems",
    "School of Nursing, Midwifery and Health Systems": "School of Nursing, Midwifery & Health Systems",
    "School of Biology and Environment Science": "School of Biology & Environmental Science",
    "School of Biology and Environmental Science": "School of Biology & Environmental Science",
    "School of Politics and Int Relations": "School of Politics and International Relations",
    "School of Languages and Literature": "School of Languages, Cultures and Linguistics",
    "Graduate School - Human Sciences": "College of Social Sciences and Law",
    "C.O. - Human Sciences": "College of Social Sciences and Law",
    "C.O. - Social Sciences and Law": "College of Social Sciences and Law",
    "School of Applied Social Science": "School of Applied Social Science (superseded in 2015)",
    "School of Information and Comms Studies": "School of Information and Communication Studies",
    "School of Soc Pol, Soc Wrk and Soc Justice": "School of Social Policy, Social Work and Social Justice",
    "School of Social Justice": "School of Social Policy, Social Work and Social Justice",
    "School of Electric, Electron and Comms Eng": "School of Electrical and Electronic Engineering",
    "School of Electrical and Electronic Eng": "School of Electrical and Electronic Engineering",
    "School of Geog, Planning and Env Policy": "School of Geography",
    "School of Geography, Planning and Environmental Policy": "School of Geography",
    "School of Biomolecular and Biomed Science": "School of Biomolecular &  Biomedical Science",
    "School of Biomolecular and Biomedical Science": "School of Biomolecular &  Biomedical Science",
    "School of Geological Sciences": "School of Earth Sciences",
    "Quinn School of Business": "School of Business",
    "Library": "UCD Library",
    "School of Agriculture, Food Science and Veterinary Medicine": "School of Agriculture and Food Science",
    "Health and Agri. Sciences": "School of Agriculture and Food Science",
    "School of Chem and Bioprocess Engineering": "School of Chemical and Bioprocess Engineering",
    "School of Languages, Cultures and Linguis": "School of Languages, Cultures and Linguistics",
    "Science Admin Office": "College of Science",
    "School of English, Drama and Film": "School of English, Drama & Film",
    "Office of Registrar": "UCD Office of the Registrar and Vice President Academic Affairs",
    "Complex and Adaptive Systems Laboratory (CASL)": "Complex and Adaptive Systems Laboratory",
    "Innovation Academy": "Institutes and Centres",
    "Access Centre": "Institutes and Centres",
    "Conway Institute of Biomolecular and Biomedical Research": "Conway Institute",
    "UCD  Centre for Animal Health Translational Research": "School of Veterinary Medicine",
    "School of Medicine and Medical Science": "School of Medicine",
    "Science Centre": "College of Science",
    "Apt 45": "CLARITY: Centre for Sensor Web Technologies",
    "10 Thomastown Road": "School of Physics",
    "Health Sciences Admin Office": "College of Health and Agricultural Sciences",
    "C.O. - Health and Agri. Sciences": "College of Health and Agricultural Sciences",

}

ucd_ns = Namespace("http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#")
swrc = SWRC("http://me.me#", open(os.path.join("output", "ucd_research.n3")))
print("===========================")
coverage = 0
authors = swrc.get_authors()
schools = swrc.get_department_names_to_uri()
print(schools)
for author in authors:
    name_page = get_page_for_name(author["lastName"] + ", " + author["firstName"])
    if name_page is not None:
        school = get_school_from_page(name_page)
        if school is not None:
            school = school.replace('&', "and").replace(" Of ", " of ")
            if school in name_mappings:
                school = name_mappings[school]
            if school in schools:
                swrc.add_affiliation(author_uri=author["uri"], organisation_uri=schools[school])
                coverage += 1
            else:
                school = "'" + school + "'"
                print("\t********************* Error 404: we lost the ", school)
swrc.output("ucd_research_depts.n3")
print("total coverage of authors in research repository: ", coverage/len(authors))