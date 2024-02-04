import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'Remove Resume Bias';
  selectedFile: File | null = null;
  redactionCompleted: boolean = false;
  fileName: any;

  constructor(private http: HttpClient) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0] as File;
  }

  callRedactionAPI() {
    if (!this.selectedFile) {
      console.error('No file selected.');
      return;
    }

    // Create a FormData object to append the file
    const formData = new FormData();
    this.fileName = this.selectedFile.name
    formData.append('pdfFile', this.selectedFile, this.selectedFile.name);
    const apiUrl = 'http://localhost:5000/api/redact';
    // Make a POST request to the Flask API endpoint for redaction
    this.http.post(apiUrl, formData).subscribe(response => {
      console.log(response);
      this.redactionCompleted = true;
      // Handle the response as needed
    });
  }
}
