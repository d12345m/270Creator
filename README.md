# 270Creator
Creates valid EDI 270 files for EMEDNY (NYS)

Known limitations and problems:

1.) The script currently creates just one transaction set, regardless of the number of NM1 segments generated. If more than 5000 NM1 segments are generated, the resultant file will not pass validation.

2.) There is NO error-checking or catching (yet).

---

The file used as input should have the following format

CIN,FirstName,LastName,DOB            
AA12345U,John,Doe,04/13/2001                
BB12345U,Jane,Doe,03/02/1965              

---

The 270_configuration.cfg file must be edited to include company-specific information (ETIN, etc).

---

The program requires two arguments to run properly:      

-i (the input file)         
-d (the destination path for the resultant .270 file)     
