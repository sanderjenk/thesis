import { Component, OnInit } from '@angular/core';
import { IssuesService } from '../issues.service';
import { Issue } from '../issue';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-selected-issues',
  templateUrl: './selected-issues.component.html',
  styleUrls: ['./selected-issues.component.css'],
})
export class SelectedIssuesComponent implements OnInit {
  generatedIssues: Issue[] = [];
  showSpinner = false;
  feedbackForm: any;
  generateForm: any;
  developers: string[] = []
  velocity: number = 0;
  constructor(private issuesService: IssuesService, private _snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.getGeneratedIssues();
    this.initFeedbackForm();
    this.initGenerateForm();
    this.getDevelopers();
  }

  initFeedbackForm() {
    this.feedbackForm = new FormGroup({
      rating: new FormControl(null, [Validators.required])
    });
  }
  
  initGenerateForm() {
    this.generateForm = new FormGroup({
      storypoints: new FormControl(null, [Validators.required]),
      developer: new FormControl(null, Validators.required)
    });
  }

  getDevelopers() {
    this.issuesService.getDevelopers().subscribe((developers: string[]) => {
      this.developers = developers;
    })
  }
  
  getGeneratedIssues() {
    this.issuesService.generatedIssuesSubject.subscribe((issues: Issue[]) => {
      this.generatedIssues = issues;
    })
  }

  generate() {
    this.showSpinner = true;
    this.issuesService.generatedIssuesSubject.next([]);
    this.issuesService.generateReccommendations(this.generateForm.value.storypoints, this.generateForm.value.developer).subscribe((issues: any) => {
      this.issuesService.generatedIssuesSubject.next(issues);
      this.showSpinner = false;
    });
  }

  getVelocity() {
    this.issuesService.getVelocity(this.generateForm.value.developer).subscribe(velocity => {
      this.velocity = velocity;
      this.generateForm.controls.storypoints.setValue(velocity);
    })
  }

  submit(){
    let value = this.feedbackForm.value;
    let data = {
      feedbackForm: value,
      generatedIssues: this.generatedIssues.map(x => x.key)
    }
    this.issuesService.submitFeedbackForm(data).subscribe(() => {
      this.openSnackBar();
    })
  }
  
  openSnackBar() {
    this._snackBar.open("Thank you", "Dismiss", {duration: 3000});
  }
}
