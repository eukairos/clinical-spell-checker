#!/usr/bin/env python3
"""
clinical_abbreviations.py
=========================
Curated lexicon of clinical abbreviations commonly found in clinical notes,
discharge summaries, and medical records. These are terms that a spellchecker
should recognise as VALID rather than flagging as errors.

Organisation:
  - Diagnosis / condition abbreviations
  - Procedure / treatment abbreviations
  - Lab / vital sign abbreviations
  - Medication-related abbreviations
  - History / documentation abbreviations
  - Anatomical abbreviations
  - Unit abbreviations
  - Ward / department abbreviations
  - Clinical scoring / assessment abbreviations
  - Common shorthand used in clinical notes

Each entry is (abbreviation, expansion, category).

Sources:
  - Joint Commission "Do Not Use" list (marked where applicable)
  - Stedman's Medical Abbreviations
  - Dorland's Medical Dictionary
  - Common usage in MIMIC-III/IV discharge summaries
  - Clinical documentation standards

Note: Some abbreviations on the Joint Commission "Do Not Use" list are still
included because they appear ubiquitously in historical clinical text. The
spellchecker needs to recognise them even if style guides discourage their use.
"""

from typing import List, Tuple

# Format: (abbreviation, expansion, category)
# All abbreviations are stored in their most common casing

CLINICAL_ABBREVIATIONS: List[Tuple[str, str, str]] = [
    # ─────────────────────────────────────────────────────────────────────
    # DIAGNOSIS / CONDITION
    # ─────────────────────────────────────────────────────────────────────
    ("AAA", "abdominal aortic aneurysm", "diagnosis"),
    ("ACS", "acute coronary syndrome", "diagnosis"),
    ("ARDS", "acute respiratory distress syndrome", "diagnosis"),
    ("AFib", "atrial fibrillation", "diagnosis"),
    ("AF", "atrial fibrillation", "diagnosis"),
    ("AKI", "acute kidney injury", "diagnosis"),
    ("AML", "acute myeloid leukemia", "diagnosis"),
    ("ALL", "acute lymphoblastic leukemia", "diagnosis"),
    ("AMS", "altered mental status", "diagnosis"),
    ("ASCVD", "atherosclerotic cardiovascular disease", "diagnosis"),
    ("ASD", "atrial septal defect", "diagnosis"),
    ("ASHD", "atherosclerotic heart disease", "diagnosis"),
    ("AVR", "aortic valve replacement", "diagnosis"),
    ("BPH", "benign prostatic hyperplasia", "diagnosis"),
    ("CAD", "coronary artery disease", "diagnosis"),
    ("CABG", "coronary artery bypass graft", "diagnosis"),
    ("CKD", "chronic kidney disease", "diagnosis"),
    ("CHF", "congestive heart failure", "diagnosis"),
    ("CLL", "chronic lymphocytic leukemia", "diagnosis"),
    ("CML", "chronic myeloid leukemia", "diagnosis"),
    ("COPD", "chronic obstructive pulmonary disease", "diagnosis"),
    ("CPAP", "continuous positive airway pressure", "diagnosis"),
    ("CVA", "cerebrovascular accident", "diagnosis"),
    ("CVD", "cardiovascular disease", "diagnosis"),
    ("DIC", "disseminated intravascular coagulation", "diagnosis"),
    ("DKA", "diabetic ketoacidosis", "diagnosis"),
    ("DM", "diabetes mellitus", "diagnosis"),
    ("DM2", "diabetes mellitus type 2", "diagnosis"),
    ("DMII", "diabetes mellitus type 2", "diagnosis"),
    ("DVT", "deep vein thrombosis", "diagnosis"),
    ("ESRD", "end-stage renal disease", "diagnosis"),
    ("ESKD", "end-stage kidney disease", "diagnosis"),
    ("ETOH", "alcohol", "diagnosis"),
    ("EtOH", "alcohol", "diagnosis"),
    ("FTT", "failure to thrive", "diagnosis"),
    ("GERD", "gastroesophageal reflux disease", "diagnosis"),
    ("GIB", "gastrointestinal bleeding", "diagnosis"),
    ("GSW", "gunshot wound", "diagnosis"),
    ("HCC", "hepatocellular carcinoma", "diagnosis"),
    ("HF", "heart failure", "diagnosis"),
    ("HFpEF", "heart failure with preserved ejection fraction", "diagnosis"),
    ("HFrEF", "heart failure with reduced ejection fraction", "diagnosis"),
    ("HIV", "human immunodeficiency virus", "diagnosis"),
    ("HTN", "hypertension", "diagnosis"),
    ("HLD", "hyperlipidemia", "diagnosis"),
    ("IBD", "inflammatory bowel disease", "diagnosis"),
    ("IBS", "irritable bowel syndrome", "diagnosis"),
    ("ICH", "intracranial hemorrhage", "diagnosis"),
    ("IDDM", "insulin-dependent diabetes mellitus", "diagnosis"),
    ("ITP", "idiopathic thrombocytopenic purpura", "diagnosis"),
    ("MI", "myocardial infarction", "diagnosis"),
    ("MDS", "myelodysplastic syndrome", "diagnosis"),
    ("MGUS", "monoclonal gammopathy of undetermined significance", "diagnosis"),
    ("MM", "multiple myeloma", "diagnosis"),
    ("MRSA", "methicillin-resistant staphylococcus aureus", "diagnosis"),
    ("MS", "multiple sclerosis", "diagnosis"),
    ("MVR", "mitral valve replacement", "diagnosis"),
    ("NIDDM", "non-insulin-dependent diabetes mellitus", "diagnosis"),
    ("NSTEMI", "non-ST elevation myocardial infarction", "diagnosis"),
    ("OA", "osteoarthritis", "diagnosis"),
    ("OSA", "obstructive sleep apnea", "diagnosis"),
    ("PAD", "peripheral arterial disease", "diagnosis"),
    ("PD", "Parkinson's disease", "diagnosis"),
    ("PE", "pulmonary embolism", "diagnosis"),
    ("PNA", "pneumonia", "diagnosis"),
    ("PUD", "peptic ulcer disease", "diagnosis"),
    ("PVD", "peripheral vascular disease", "diagnosis"),
    ("RA", "rheumatoid arthritis", "diagnosis"),
    ("RLL", "right lower lobe", "diagnosis"),
    ("RML", "right middle lobe", "diagnosis"),
    ("RUL", "right upper lobe", "diagnosis"),
    ("LLL", "left lower lobe", "diagnosis"),
    ("LUL", "left upper lobe", "diagnosis"),
    ("SAH", "subarachnoid hemorrhage", "diagnosis"),
    ("SBO", "small bowel obstruction", "diagnosis"),
    ("SCA", "sickle cell anemia", "diagnosis"),
    ("SCC", "squamous cell carcinoma", "diagnosis"),
    ("SIADH", "syndrome of inappropriate antidiuretic hormone", "diagnosis"),
    ("SLE", "systemic lupus erythematosus", "diagnosis"),
    ("SOB", "shortness of breath", "diagnosis"),
    ("STEMI", "ST elevation myocardial infarction", "diagnosis"),
    ("TIA", "transient ischemic attack", "diagnosis"),
    ("TB", "tuberculosis", "diagnosis"),
    ("TBI", "traumatic brain injury", "diagnosis"),
    ("UC", "ulcerative colitis", "diagnosis"),
    ("URI", "upper respiratory infection", "diagnosis"),
    ("UTI", "urinary tract infection", "diagnosis"),
    ("VRE", "vancomycin-resistant enterococcus", "diagnosis"),
    ("VSD", "ventricular septal defect", "diagnosis"),
    ("VTE", "venous thromboembolism", "diagnosis"),

    # ─────────────────────────────────────────────────────────────────────
    # PROCEDURES / TREATMENTS
    # ─────────────────────────────────────────────────────────────────────
    ("ABG", "arterial blood gas", "procedure"),
    ("AED", "automated external defibrillator", "procedure"),
    ("BiPAP", "bilevel positive airway pressure", "procedure"),
    ("BMP", "basic metabolic panel", "procedure"),
    ("CBC", "complete blood count", "procedure"),
    ("CMP", "comprehensive metabolic panel", "procedure"),
    ("CRRT", "continuous renal replacement therapy", "procedure"),
    ("CT", "computed tomography", "procedure"),
    ("CTA", "computed tomography angiography", "procedure"),
    ("CVC", "central venous catheter", "procedure"),
    ("CXR", "chest x-ray", "procedure"),
    ("D/C", "discontinue or discharge", "procedure"),
    ("D&C", "dilation and curettage", "procedure"),
    ("ECMO", "extracorporeal membrane oxygenation", "procedure"),
    ("ECG", "electrocardiogram", "procedure"),
    ("EEG", "electroencephalogram", "procedure"),
    ("EGD", "esophagogastroduodenoscopy", "procedure"),
    ("EKG", "electrocardiogram", "procedure"),
    ("EMG", "electromyography", "procedure"),
    ("ERCP", "endoscopic retrograde cholangiopancreatography", "procedure"),
    ("ETT", "endotracheal tube", "procedure"),
    ("FOBT", "fecal occult blood test", "procedure"),
    ("HD", "hemodialysis", "procedure"),
    ("IABP", "intra-aortic balloon pump", "procedure"),
    ("ICD", "implantable cardioverter-defibrillator", "procedure"),
    ("ICP", "intracranial pressure", "procedure"),
    ("INR", "international normalised ratio", "procedure"),
    ("IVUS", "intravascular ultrasound", "procedure"),
    ("KUB", "kidneys ureters bladder (x-ray)", "procedure"),
    ("LP", "lumbar puncture", "procedure"),
    ("MRA", "magnetic resonance angiography", "procedure"),
    ("MRI", "magnetic resonance imaging", "procedure"),
    ("NG", "nasogastric", "procedure"),
    ("NGT", "nasogastric tube", "procedure"),
    ("ORIF", "open reduction internal fixation", "procedure"),
    ("PCI", "percutaneous coronary intervention", "procedure"),
    ("PEG", "percutaneous endoscopic gastrostomy", "procedure"),
    ("PFT", "pulmonary function test", "procedure"),
    ("PICC", "peripherally inserted central catheter", "procedure"),
    ("PPM", "permanent pacemaker", "procedure"),
    ("PT", "physical therapy", "procedure"),
    ("PTCA", "percutaneous transluminal coronary angioplasty", "procedure"),
    ("RRT", "rapid response team", "procedure"),
    ("TEE", "transesophageal echocardiography", "procedure"),
    ("TIPS", "transjugular intrahepatic portosystemic shunt", "procedure"),
    ("TKA", "total knee arthroplasty", "procedure"),
    ("TKR", "total knee replacement", "procedure"),
    ("THA", "total hip arthroplasty", "procedure"),
    ("THR", "total hip replacement", "procedure"),
    ("TPN", "total parenteral nutrition", "procedure"),
    ("TTE", "transthoracic echocardiography", "procedure"),
    ("TURP", "transurethral resection of the prostate", "procedure"),
    ("US", "ultrasound", "procedure"),
    ("VATS", "video-assisted thoracoscopic surgery", "procedure"),
    ("XRT", "radiation therapy", "procedure"),

    # ─────────────────────────────────────────────────────────────────────
    # LAB VALUES / VITAL SIGNS
    # ─────────────────────────────────────────────────────────────────────
    ("ABG", "arterial blood gas", "lab"),
    ("AFP", "alpha-fetoprotein", "lab"),
    ("ALT", "alanine aminotransferase", "lab"),
    ("ANA", "antinuclear antibody", "lab"),
    ("ANC", "absolute neutrophil count", "lab"),
    ("APTT", "activated partial thromboplastin time", "lab"),
    ("AST", "aspartate aminotransferase", "lab"),
    ("BG", "blood glucose", "lab"),
    ("BNP", "brain natriuretic peptide", "lab"),
    ("BP", "blood pressure", "lab"),
    ("BUN", "blood urea nitrogen", "lab"),
    ("CA", "calcium", "lab"),
    ("CEA", "carcinoembryonic antigen", "lab"),
    ("Cr", "creatinine", "lab"),
    ("CRP", "C-reactive protein", "lab"),
    ("D-dimer", "D-dimer", "lab"),
    ("eGFR", "estimated glomerular filtration rate", "lab"),
    ("ESR", "erythrocyte sedimentation rate", "lab"),
    ("FBS", "fasting blood sugar", "lab"),
    ("FiO2", "fraction of inspired oxygen", "lab"),
    ("GFR", "glomerular filtration rate", "lab"),
    ("Hb", "hemoglobin", "lab"),
    ("HbA1c", "glycated hemoglobin", "lab"),
    ("Hct", "hematocrit", "lab"),
    ("HDL", "high-density lipoprotein", "lab"),
    ("Hgb", "hemoglobin", "lab"),
    ("HR", "heart rate", "lab"),
    ("K", "potassium", "lab"),
    ("LDH", "lactate dehydrogenase", "lab"),
    ("LDL", "low-density lipoprotein", "lab"),
    ("LFT", "liver function test", "lab"),
    ("LFTs", "liver function tests", "lab"),
    ("Lytes", "electrolytes", "lab"),
    ("MAP", "mean arterial pressure", "lab"),
    ("Mg", "magnesium", "lab"),
    ("Na", "sodium", "lab"),
    ("NT-proBNP", "N-terminal pro-brain natriuretic peptide", "lab"),
    ("O2", "oxygen", "lab"),
    ("O2sat", "oxygen saturation", "lab"),
    ("pCO2", "partial pressure of carbon dioxide", "lab"),
    ("pH", "pH", "lab"),
    ("Plt", "platelets", "lab"),
    ("Plts", "platelets", "lab"),
    ("PO2", "partial pressure of oxygen", "lab"),
    ("pO2", "partial pressure of oxygen", "lab"),
    ("PSA", "prostate-specific antigen", "lab"),
    ("PT", "prothrombin time", "lab"),
    ("PTT", "partial thromboplastin time", "lab"),
    ("RBC", "red blood cell", "lab"),
    ("RR", "respiratory rate", "lab"),
    ("SaO2", "arterial oxygen saturation", "lab"),
    ("SBP", "systolic blood pressure", "lab"),
    ("DBP", "diastolic blood pressure", "lab"),
    ("SpO2", "peripheral oxygen saturation", "lab"),
    ("T", "temperature", "lab"),
    ("Tbili", "total bilirubin", "lab"),
    ("TG", "triglycerides", "lab"),
    ("Tmax", "maximum temperature", "lab"),
    ("Trop", "troponin", "lab"),
    ("TSH", "thyroid-stimulating hormone", "lab"),
    ("UA", "urinalysis", "lab"),
    ("UOP", "urine output", "lab"),
    ("WBC", "white blood cell", "lab"),

    # ─────────────────────────────────────────────────────────────────────
    # MEDICATION-RELATED
    # ─────────────────────────────────────────────────────────────────────
    ("ABX", "antibiotics", "medication"),
    ("ACEi", "ACE inhibitor", "medication"),
    ("ACEI", "ACE inhibitor", "medication"),
    ("ARB", "angiotensin receptor blocker", "medication"),
    ("ASA", "aspirin (acetylsalicylic acid)", "medication"),
    ("BB", "beta blocker", "medication"),
    ("BID", "twice daily (bis in die)", "medication"),
    ("CCB", "calcium channel blocker", "medication"),
    ("DDI", "drug-drug interaction", "medication"),
    ("DOAC", "direct oral anticoagulant", "medication"),
    ("NOAC", "novel oral anticoagulant", "medication"),
    ("D5W", "5% dextrose in water", "medication"),
    ("D5NS", "5% dextrose in normal saline", "medication"),
    ("DSW", "dextrose in sterile water", "medication"),
    ("EPO", "erythropoietin", "medication"),
    ("ER", "extended release", "medication"),
    ("GCSF", "granulocyte colony-stimulating factor", "medication"),
    ("G-CSF", "granulocyte colony-stimulating factor", "medication"),
    ("gtt", "drops (guttae)", "medication"),
    ("gtts", "drops (guttae)", "medication"),
    ("HCTZ", "hydrochlorothiazide", "medication"),
    ("HS", "at bedtime (hora somni)", "medication"),
    ("IM", "intramuscular", "medication"),
    ("INH", "isoniazid", "medication"),
    ("IU", "international unit", "medication"),
    ("IV", "intravenous", "medication"),
    ("IVF", "intravenous fluids", "medication"),
    ("IVPB", "intravenous piggyback", "medication"),
    ("KCl", "potassium chloride", "medication"),
    ("LR", "lactated Ringer's", "medication"),
    ("MAOi", "monoamine oxidase inhibitor", "medication"),
    ("MDI", "metered-dose inhaler", "medication"),
    ("MgSO4", "magnesium sulfate", "medication"),
    ("MVI", "multivitamin", "medication"),
    ("NaCl", "sodium chloride", "medication"),
    ("NKDA", "no known drug allergies", "medication"),
    ("NKA", "no known allergies", "medication"),
    ("NSAID", "nonsteroidal anti-inflammatory drug", "medication"),
    ("NSAIDs", "nonsteroidal anti-inflammatory drugs", "medication"),
    ("NS", "normal saline", "medication"),
    ("NTG", "nitroglycerin", "medication"),
    ("OTC", "over the counter", "medication"),
    ("PCA", "patient-controlled analgesia", "medication"),
    ("PCN", "penicillin", "medication"),
    ("PO", "by mouth (per os)", "medication"),
    ("PPI", "proton pump inhibitor", "medication"),
    ("PPIs", "proton pump inhibitors", "medication"),
    ("PRN", "as needed (pro re nata)", "medication"),
    ("prn", "as needed (pro re nata)", "medication"),
    ("q4h", "every 4 hours", "medication"),
    ("q6h", "every 6 hours", "medication"),
    ("q8h", "every 8 hours", "medication"),
    ("q12h", "every 12 hours", "medication"),
    ("QD", "once daily (quaque die)", "medication"),
    ("QHS", "at bedtime", "medication"),
    ("QID", "four times daily", "medication"),
    ("QOD", "every other day", "medication"),
    ("Rx", "prescription or treatment", "medication"),
    ("SC", "subcutaneous", "medication"),
    ("SL", "sublingual", "medication"),
    ("SQ", "subcutaneous", "medication"),
    ("SSRI", "selective serotonin reuptake inhibitor", "medication"),
    ("SSRIs", "selective serotonin reuptake inhibitors", "medication"),
    ("TCA", "tricyclic antidepressant", "medication"),
    ("TCAs", "tricyclic antidepressants", "medication"),
    ("TID", "three times daily (ter in die)", "medication"),
    ("TMP-SMX", "trimethoprim-sulfamethoxazole", "medication"),
    ("tPA", "tissue plasminogen activator", "medication"),
    ("UFH", "unfractionated heparin", "medication"),
    ("LMWH", "low-molecular-weight heparin", "medication"),
    ("VPA", "valproic acid", "medication"),

    # ─────────────────────────────────────────────────────────────────────
    # HISTORY / DOCUMENTATION / CLINICAL WORKFLOW
    # ─────────────────────────────────────────────────────────────────────
    ("AMA", "against medical advice", "documentation"),
    ("BRBPR", "bright red blood per rectum", "documentation"),
    ("c/o", "complains of", "documentation"),
    ("CC", "chief complaint", "documentation"),
    ("d/c", "discharge or discontinue", "documentation"),
    ("D/C", "discharge or discontinue", "documentation"),
    ("DNR", "do not resuscitate", "documentation"),
    ("DNI", "do not intubate", "documentation"),
    ("DOE", "dyspnea on exertion", "documentation"),
    ("DTR", "deep tendon reflex", "documentation"),
    ("DTRs", "deep tendon reflexes", "documentation"),
    ("Dx", "diagnosis", "documentation"),
    ("dx", "diagnosis", "documentation"),
    ("ED", "emergency department", "documentation"),
    ("ER", "emergency room", "documentation"),
    ("FHx", "family history", "documentation"),
    ("f/u", "follow-up", "documentation"),
    ("GCS", "Glasgow Coma Scale", "documentation"),
    ("GOC", "goals of care", "documentation"),
    ("H&P", "history and physical", "documentation"),
    ("HPI", "history of present illness", "documentation"),
    ("Hx", "history", "documentation"),
    ("hx", "history", "documentation"),
    ("I&D", "incision and drainage", "documentation"),
    ("I/O", "intake and output", "documentation"),
    ("ICU", "intensive care unit", "documentation"),
    ("LOS", "length of stay", "documentation"),
    ("MICU", "medical intensive care unit", "documentation"),
    ("SICU", "surgical intensive care unit", "documentation"),
    ("CCU", "coronary care unit", "documentation"),
    ("NICU", "neonatal intensive care unit", "documentation"),
    ("PICU", "pediatric intensive care unit", "documentation"),
    ("NAD", "no acute distress", "documentation"),
    ("NPO", "nothing by mouth (nil per os)", "documentation"),
    ("npo", "nothing by mouth (nil per os)", "documentation"),
    ("NKDA", "no known drug allergies", "documentation"),
    ("OOB", "out of bed", "documentation"),
    ("OR", "operating room", "documentation"),
    ("PACU", "post-anesthesia care unit", "documentation"),
    ("PE", "physical examination", "documentation"),
    ("PMHx", "past medical history", "documentation"),
    ("PMH", "past medical history", "documentation"),
    ("PSHx", "past surgical history", "documentation"),
    ("PSH", "past surgical history", "documentation"),
    ("Pt", "patient", "documentation"),
    ("pt", "patient", "documentation"),
    ("ROS", "review of systems", "documentation"),
    ("Rx", "prescription", "documentation"),
    ("rx", "prescription", "documentation"),
    ("s/p", "status post", "documentation"),
    ("S/P", "status post", "documentation"),
    ("Sx", "symptoms", "documentation"),
    ("sx", "symptoms", "documentation"),
    ("Tx", "treatment", "documentation"),
    ("tx", "treatment", "documentation"),
    ("VS", "vital signs", "documentation"),
    ("w/u", "workup", "documentation"),
    ("WNL", "within normal limits", "documentation"),
    ("wnl", "within normal limits", "documentation"),
    ("yo", "year old", "documentation"),
    ("y/o", "year old", "documentation"),
    ("YO", "year old", "documentation"),
    ("POD", "postoperative day", "documentation"),
    ("POD#1", "postoperative day 1", "documentation"),
    ("postop", "postoperative", "documentation"),
    ("preop", "preoperative", "documentation"),

    # ─────────────────────────────────────────────────────────────────────
    # ANATOMY / BODY SYSTEMS
    # ─────────────────────────────────────────────────────────────────────
    ("abd", "abdomen", "anatomy"),
    ("bilat", "bilateral", "anatomy"),
    ("CNS", "central nervous system", "anatomy"),
    ("CSF", "cerebrospinal fluid", "anatomy"),
    ("CVS", "cardiovascular system", "anatomy"),
    ("ENT", "ear nose and throat", "anatomy"),
    ("ext", "extremities", "anatomy"),
    ("GI", "gastrointestinal", "anatomy"),
    ("GU", "genitourinary", "anatomy"),
    ("HEENT", "head ears eyes nose throat", "anatomy"),
    ("LLQ", "left lower quadrant", "anatomy"),
    ("LUQ", "left upper quadrant", "anatomy"),
    ("MSK", "musculoskeletal", "anatomy"),
    ("neuro", "neurological", "anatomy"),
    ("OB/GYN", "obstetrics and gynecology", "anatomy"),
    ("PERRLA", "pupils equal round reactive to light and accommodation", "anatomy"),
    ("PNS", "peripheral nervous system", "anatomy"),
    ("RLQ", "right lower quadrant", "anatomy"),
    ("ROM", "range of motion", "anatomy"),
    ("RUQ", "right upper quadrant", "anatomy"),

    # ─────────────────────────────────────────────────────────────────────
    # UNITS
    # ─────────────────────────────────────────────────────────────────────
    ("bpm", "beats per minute", "unit"),
    ("cc", "cubic centimeters", "unit"),
    ("cm", "centimeters", "unit"),
    ("dL", "deciliter", "unit"),
    ("gm", "grams", "unit"),
    ("hr", "hour", "unit"),
    ("kcal", "kilocalorie", "unit"),
    ("kg", "kilograms", "unit"),
    ("L", "liters", "unit"),
    ("lb", "pounds", "unit"),
    ("mcg", "micrograms", "unit"),
    ("mCi", "millicurie", "unit"),
    ("mEq", "milliequivalent", "unit"),
    ("mg", "milligrams", "unit"),
    ("mIU", "milli-international unit", "unit"),
    ("mL", "milliliters", "unit"),
    ("mm", "millimeters", "unit"),
    ("mmHg", "millimeters of mercury", "unit"),
    ("mmol", "millimoles", "unit"),
    ("mosm", "milliosmoles", "unit"),
    ("mOsm", "milliosmoles", "unit"),
    ("ng", "nanograms", "unit"),
    ("nmol", "nanomoles", "unit"),
    ("pg", "picograms", "unit"),
    ("U", "units", "unit"),
    ("uL", "microliters", "unit"),
    ("umol", "micromoles", "unit"),

    # ─────────────────────────────────────────────────────────────────────
    # CLINICAL SCORING / ASSESSMENT
    # ─────────────────────────────────────────────────────────────────────
    ("APACHE", "Acute Physiology and Chronic Health Evaluation", "scoring"),
    ("APGAR", "Appearance Pulse Grimace Activity Respiration", "scoring"),
    ("BMI", "body mass index", "scoring"),
    ("BSA", "body surface area", "scoring"),
    ("CHADS2", "cardiac failure hypertension age diabetes stroke", "scoring"),
    ("CHA2DS2-VASc", "congestive HF HTN age DM stroke vascular disease", "scoring"),
    ("CURB-65", "confusion urea RR BP age>=65", "scoring"),
    ("GCS", "Glasgow Coma Scale", "scoring"),
    ("HAS-BLED", "bleeding risk score", "scoring"),
    ("MELD", "Model for End-Stage Liver Disease", "scoring"),
    ("NIHSS", "NIH Stroke Scale", "scoring"),
    ("NYHA", "New York Heart Association", "scoring"),
    ("SOFA", "Sequential Organ Failure Assessment", "scoring"),
    ("TIMI", "Thrombolysis in Myocardial Infarction", "scoring"),
    ("Wells", "Wells score (DVT/PE probability)", "scoring"),

    # ─────────────────────────────────────────────────────────────────────
    # COMMON CLINICAL SHORTHAND (discharge summaries, progress notes)
    # ─────────────────────────────────────────────────────────────────────
    ("afebrile", "without fever", "shorthand"),
    ("approx", "approximately", "shorthand"),
    ("assoc", "associated", "shorthand"),
    ("bilat", "bilateral", "shorthand"),
    ("BKA", "below-knee amputation", "shorthand"),
    ("AKA", "above-knee amputation", "shorthand"),
    ("BLE", "bilateral lower extremities", "shorthand"),
    ("BUE", "bilateral upper extremities", "shorthand"),
    ("c/w", "consistent with", "shorthand"),
    ("CP", "chest pain", "shorthand"),
    ("defib", "defibrillation", "shorthand"),
    ("decr", "decreased", "shorthand"),
    ("diff", "differential", "shorthand"),
    ("dispo", "disposition", "shorthand"),
    ("dtr", "deep tendon reflex", "shorthand"),
    ("eval", "evaluation", "shorthand"),
    ("freq", "frequency", "shorthand"),
    ("fx", "fracture", "shorthand"),
    ("heplock", "heparin lock", "shorthand"),
    ("incr", "increased", "shorthand"),
    ("infxn", "infection", "shorthand"),
    ("irreg", "irregular", "shorthand"),
    ("LE", "lower extremity", "shorthand"),
    ("LLE", "left lower extremity", "shorthand"),
    ("LUE", "left upper extremity", "shorthand"),
    ("RLE", "right lower extremity", "shorthand"),
    ("RUE", "right upper extremity", "shorthand"),
    ("UE", "upper extremity", "shorthand"),
    ("meds", "medications", "shorthand"),
    ("neg", "negative", "shorthand"),
    ("nml", "normal", "shorthand"),
    ("occ", "occasional", "shorthand"),
    ("palp", "palpable", "shorthand"),
    ("pos", "positive", "shorthand"),
    ("prog", "prognosis", "shorthand"),
    ("pt", "patient", "shorthand"),
    ("r/o", "rule out", "shorthand"),
    ("R/O", "rule out", "shorthand"),
    ("sig", "significant", "shorthand"),
    ("subq", "subcutaneous", "shorthand"),
    ("sxs", "symptoms", "shorthand"),
    ("trach", "tracheostomy", "shorthand"),
    ("u/s", "ultrasound", "shorthand"),
    ("w/", "with", "shorthand"),
    ("w/o", "without", "shorthand"),
    ("wt", "weight", "shorthand"),
    ("ht", "height", "shorthand"),

    # ─────────────────────────────────────────────────────────────────────
    # INFECTIOUS DISEASE
    # ─────────────────────────────────────────────────────────────────────
    ("SARS", "severe acute respiratory syndrome", "infectious_disease"),
    ("COVID", "coronavirus disease", "infectious_disease"),
    ("COVID-19", "coronavirus disease 2019", "infectious_disease"),
    ("RSV", "respiratory syncytial virus", "infectious_disease"),
    ("CMV", "cytomegalovirus", "infectious_disease"),
    ("EBV", "Epstein-Barr virus", "infectious_disease"),
    ("HBV", "hepatitis B virus", "infectious_disease"),
    ("HCV", "hepatitis C virus", "infectious_disease"),
    ("HAV", "hepatitis A virus", "infectious_disease"),
    ("HSV", "herpes simplex virus", "infectious_disease"),
    ("VZV", "varicella-zoster virus", "infectious_disease"),
    ("MERS", "Middle East respiratory syndrome", "infectious_disease"),
    ("CDI", "Clostridioides difficile infection", "infectious_disease"),
    ("C.diff", "Clostridioides difficile", "infectious_disease"),
    ("C diff", "Clostridioides difficile", "infectious_disease"),
    ("ESBL", "extended-spectrum beta-lactamase", "infectious_disease"),
    ("CRE", "carbapenem-resistant Enterobacteriaceae", "infectious_disease"),

    # ─────────────────────────────────────────────────────────────────────
    # IMAGING / RADIOLOGY
    # ─────────────────────────────────────────────────────────────────────
    ("AP", "anteroposterior", "imaging"),
    ("PA", "posteroanterior", "imaging"),
    ("lat", "lateral", "imaging"),
    ("FLAIR", "fluid-attenuated inversion recovery", "imaging"),
    ("DWI", "diffusion-weighted imaging", "imaging"),
    ("ADC", "apparent diffusion coefficient", "imaging"),
    ("SUV", "standardized uptake value", "imaging"),
    ("PET", "positron emission tomography", "imaging"),
    ("SPECT", "single-photon emission computed tomography", "imaging"),
    ("DEXA", "dual-energy X-ray absorptiometry", "imaging"),
    ("DXA", "dual-energy X-ray absorptiometry", "imaging"),
    ("HRCT", "high-resolution computed tomography", "imaging"),
]


def get_abbreviations() -> List[Tuple[str, str, str]]:
    """Return the full abbreviation list."""
    return CLINICAL_ABBREVIATIONS


def get_abbreviation_tokens() -> set:
    """Return just the abbreviation strings (for dictionary inclusion)."""
    return {abbr for abbr, _, _ in CLINICAL_ABBREVIATIONS}


def get_expansion_tokens() -> set:
    """Return all unique words from expansions (excluding parenthetical Latin)."""
    import re
    # Remove parenthetical content like "(bis in die)", "(per os)"
    paren_re = re.compile(r"\([^)]*\)")
    tokens = set()
    for _, expansion, _ in CLINICAL_ABBREVIATIONS:
        cleaned = paren_re.sub("", expansion).strip()
        for word in cleaned.split():
            word = word.strip(".,;:()")
            if len(word) >= 2 and word.isalpha():
                tokens.add(word.lower())
    return tokens


def get_abbreviations_by_category() -> dict:
    """Return abbreviations grouped by category."""
    by_cat = {}
    for abbr, expansion, category in CLINICAL_ABBREVIATIONS:
        by_cat.setdefault(category, []).append((abbr, expansion))
    return by_cat


def write_abbreviations_tsv(output_path: str):
    """Write abbreviations to a TSV file."""
    import csv

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["abbreviation", "expansion", "category"])
        for abbr, expansion, category in sorted(CLINICAL_ABBREVIATIONS):
            writer.writerow([abbr, expansion, category])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export clinical abbreviations")
    parser.add_argument("--output", default="clinical_abbreviations.tsv")
    parser.add_argument("--stats", action="store_true", help="Print category statistics")
    args = parser.parse_args()

    write_abbreviations_tsv(args.output)
    print(f"Wrote {len(CLINICAL_ABBREVIATIONS)} abbreviations to {args.output}")

    if args.stats:
        by_cat = get_abbreviations_by_category()
        print("\nAbbreviations by category:")
        for cat in sorted(by_cat, key=lambda c: -len(by_cat[c])):
            print(f"  {cat:<25s} {len(by_cat[cat]):>5}")
        print(f"  {'TOTAL':<25s} {len(CLINICAL_ABBREVIATIONS):>5}")
        print(f"\nUnique abbreviation tokens: {len(get_abbreviation_tokens())}")
        print(f"Unique expansion words:     {len(get_expansion_tokens())}")
