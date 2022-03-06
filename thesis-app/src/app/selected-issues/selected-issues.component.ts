import { Component, OnInit } from '@angular/core';
import { IssuesService } from '../issues/issues.service';
import { Issue } from '../issues/issue';

@Component({
  selector: 'app-selected-issues',
  templateUrl: './selected-issues.component.html',
  styleUrls: ['./selected-issues.component.css'],
})
export class SelectedIssuesComponent implements OnInit {
  selectedIssues: Issue[] = [];

  generatedIssues: Issue[] = [];


  constructor(private issuesService: IssuesService) { }

  ngOnInit(): void {
    this.getIssues();
  }

  getIssues() {
    this.issuesService.issueHistorySubject.subscribe((issues: Issue[]) => {
      this.selectedIssues = issues;
    })
  }

  remove(issue: Issue) {
    this.issuesService.remove(issue.key); 
  }

  generate() {
    this.issuesService.generateReccommendations(this.selectedIssues).subscribe((issues: Issue[]) => {
      this.generatedIssues = issues;
    })
  }
}
