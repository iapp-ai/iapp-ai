
var request = require('request');
var fs = require('fs');
var path = require('path');
const apikey = '';

class iapp_ai {
    constructor(apikey) {
        this.apikey = apikey;
    }
    /* Image Recognition */
    // idcard front ocr
    async idcardFront_Ocr(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/thai-national-id-card/v3/front',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // idcard front photocopied ocr
    async idcardFront_photocopied(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/thai-national-id-card-with-signature/front',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // idcard back ocr
    async idcardBack_Ocr(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/thai-national-id-card/v3.5/back',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Thai Plate Number OCR API
    async lpr_ocr(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/license-plate-recognition/file',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Thai BookBank OCR API
    async bookbank_ocr(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/book-bank-ocr/file',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // [NEW] Passport OCR API: Detect ZMR Only
    async passport_ocr(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/passport-ocr/ocr',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
     // [NEW] Thai Driver License OCR API
    async driverLicense_ocr(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/thai-driver-license-ocr',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                return response.body;
            });
        })
    }
    // [NEW] Document OCR API: return Plain text
    async document_ocr_plaintext(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/document-ocr/ocr',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // [NEW] Document OCR API: return JSON LAYOUT
    async document_ocr_jsonlayout(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/document-ocr/layout',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // [NEW] Document OCR API: return as DOCX
    async document_ocr_docx(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/document-ocr/docx',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(response.body)
                
            });
        })
    }
    // Image Background Removal
    // File Support
    async remove_bg_file(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face-extractor/predict/file',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            },
            'rotateIfPortrait': 'true'
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(response.body)
                
            },
            );
        })
    }

    // Water Meter OCR
    async waterMeter_file(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/meter-number-ocr/file',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                return response.body;
            });
        })
    }


    // Power Meter OCR

    // Face Liveness Detection

    // Face Verification
    async face_verification(filepath1, filepath2) {
        var filename1 = path.basename(filepath1);
        var filename2 = path.basename(filepath2);
        var options = {
            'method': 'POST',
            'url':  'https://api.iapp.co.th/face_compare',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file1': {
                  'value': fs.createReadStream(filepath1),
                  'options': {
                    'filename': filename1,
                    'contentType': null
                  }
                },
                'file2': {
                  'value': fs.createReadStream(filepath2),
                  'options': {
                    'filename': filename2,
                    'contentType': null
                  }
                }
              }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
        // Face Verification Configuration
    async face_ver_config(company_name = company_name, password = password) {
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_config_score',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'company': String(company_name),
                'password': String(password)
              }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }

    // Face Detection
        // Single Face Detection
    async face_detect_single(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_detect_single',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
        // Multi Face Detection
    async face_detect_multi(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_detect_multi',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
        // Face Detection Configuration
    async face_detect_config(company_name = company_name, password = password) {
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_config_score',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'company': String(company_name),
                'password': String(password)
              }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }

    // Face Recognition
        // Single Face Recognition
    async face_recog_single(filepath=filepath, company_name=company_name) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_single',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    },
                },
                'company': String(company_name)
            },
            
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
        // Multi Face Recognition
    async face_recog_multi(filepath=filepath, company_name=company_name) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_multi',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                },
                'company': String(company_name)
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Face Crop
    async face_recog_facecrop(filepath=filepath, company_name=company_name) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_facecrop',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                },
                'company': String(company_name)
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Face Add
    async face_recog_add(filepath=filepath, company_name=company_name, person_name=person_name, password=password) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_add',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                },
                'company': String(company_name),
                'name': String(person_name),
                'password': String(password)
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Face Import
    async face_recog_import(filepath=filepath, company_name=company_name, password=password) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_import',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                },
                'company': String(company_name),
                'password': String(password)
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Face Export
    async face_recog_export(company_name=company_name, password=password, type_file=type_file) {
        
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_export',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'company': String(company_name),
                'password': String(password),
                'type_file': String(type_file),
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(response.body)
                
            });
        })
    }
    // Face Check
    async face_recog_check(company_name=company_name, password=password) {
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_check',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'company': String(company_name),
                'password': String(password),
                
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Face Removal
    async face_recog_remove(company_name=company_name, password=password, person_name=person_name, face_id=face_id) {
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_recog_remove',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'company': String(company_name),
                'password': String(password),
                'name': String(person_name),
                'face_id': String(face_id)
                
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }
    // Reset Password
    async face_reset_password(company_name=company_name, old_password=old_password, new_password=new_password) {
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/password/change',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'company': String(company_name),
                'old_password': String(old_password),
                'new_password': String(new_password)
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }

    // Face Recognition Configuration
    async face_recog_config(company_name = company_name, password = password) {
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/face_config_score',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'company': String(company_name),
                'password': String(password)
              }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }


    /* Voice and Speech */
    // TTS: Kaitom voice
    async kaitom_tts(text) {
        var thaitext = String(text);
        var url = 'https://api.iapp.co.th/thai-tts-kaitom/tts?text=' + thaitext;
        var options = {
            'method': 'GET',
            'url': encodeURI(url),
            'headers': {
                'apikey': this.apikey
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(response.body)
                
            });
        })
    }

    // TTS: Cee voice
    async cee_tts(text) {
        var thaitext = String(text);
        var url = 'https://api.iapp.co.th/thai-tts-kaitom/tts?text=' + thaitext;
        var options = {
            'method': 'GET',
            'url': encodeURI(url),
            'headers': {
                'apikey': this.apikey
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(response.body)
                
            });
        })
    }
    // ASR
    async thai_asr(filepath) {
        var filename = path.basename(filepath);
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/asr',
            'headers': {
                'apikey': this.apikey
            },
            formData: {
                'file': {
                    'value': fs.createReadStream(filepath),
                    'options': {
                        'filename': filename,
                        'contentType': null
                    }
                }
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }

    /* Thai Natural Language Processing */
    // Thai Question & Answer
    async thai_qa(question = question, document = document) {
        var options = {
            'method': 'POST',
            'url': 'https://api.iapp.co.th/thai-qa/inference',
            'headers': {
                'Content-Type': 'application/json',
                'apikey': this.apikey
            },
            body: JSON.stringify({
                "question": question,
                "document": document
            })

        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(response.body)
                
            });
        })
    }
    // Thai Text Summary API
    async thai_text_sum(text = text) {
        var text = text.replace(/\s/g, '');
        var output_length;
        var url = String('https://api.iapp.co.th/text-summarization?text=' + text + '&output_length=84');
        var options = {
            'method': 'GET',
            'url': encodeURI(url),
            'headers': {
                'Content-Type': 'application/json',
                'apikey': this.apikey
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }

    // Thai Question Generator API
    async thai_qgen(text = text) {
        var text = text.replace(/\s/g, '');
        var url = String('http://api.iapp.co.th/qa-generator-th?text=' + text + '&apikey=' + this.apikey);
        var options = {
            'method': 'GET',
            'url': encodeURI(url),
            'headers': {
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }

    // Thai/English Machine Translation API
    async eng_thai_translate(text = text) {
        var text = text.replace(/\s/g, '');
        var url = String('https://api.iapp.co.th/translate/auto?text=' + text);
        var options = {
            'method': 'GET',
            'url': encodeURI(url),
            'headers': {
                apikey: this.apikey
            }
        };
        return new Promise((resolve, reject) => {
            request(options, function (error, response) {
                if (error) reject(error);
                resolve(JSON.parse(response.body))
                
            });
        })
    }

}

module.exports = iapp_ai;
