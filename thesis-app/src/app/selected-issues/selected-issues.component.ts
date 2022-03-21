import { Component, OnInit } from '@angular/core';
import { IssuesService } from '../issues/issues.service';
import { Issue } from '../issues/issue';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Xliff } from '@angular/compiler';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-selected-issues',
  templateUrl: './selected-issues.component.html',
  styleUrls: ['./selected-issues.component.css'],
})
export class SelectedIssuesComponent implements OnInit {
  selectedIssues: Issue[] = [];
  selectedIssuesCount = 0;
  generatedIssues: Issue[] = [];
  showSpinner = false;
  feedbackForm: any;
  generateForm: any;

  constructor(private issuesService: IssuesService, private _snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.getIssues();
    this.getGeneratedIssues();
    this.getSelectedIssuesCount();

    this.initFeedbackForm();

    this.initGenerateForm();
  }

  initFeedbackForm() {
    this.feedbackForm = new FormGroup({
      rating: new FormControl(null, [Validators.required])
    });
  }

  
  initGenerateForm() {
    this.generateForm = new FormGroup({
      storypoints: new FormControl(10, [Validators.required])
    });
  }

  getIssues() {
    this.issuesService.issueHistorySubject.subscribe((issues: Issue[]) => {
      this.selectedIssues = issues;
    })
  }
  
  getGeneratedIssues() {
    this.issuesService.generatedIssuesSubject.subscribe((issues: Issue[]) => {
      this.generatedIssues = issues;
    })
  }

  remove(issue: Issue) {
    this.issuesService.remove(issue.key); 
    this.issuesService.generatedIssuesSubject.next([]);
  }

  generate() {
    this.showSpinner = true;
    this.issuesService.generatedIssuesSubject.next([]);
    this.issuesService.generateReccommendations(this.selectedIssues, this.generateForm.value.storypoints).subscribe((issues: Issue[]) => {
      this.issuesService.generatedIssuesSubject.next(issues);
      this.showSpinner = false;
    });
  }

  getSelectedIssuesCount() {
    this.issuesService.issueHistorySubject.subscribe(x => this.selectedIssuesCount = x.length);
  }

  submit(){
    let value = this.feedbackForm.value;
    let data = {
      feedbackForm: value,
      selectedIssues: this.selectedIssues.map(x => x.key),
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
