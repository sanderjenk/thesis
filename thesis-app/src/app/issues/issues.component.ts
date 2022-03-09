import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Issue } from './issue';
import { IssuesService } from './issues.service';

@Component({
  selector: 'app-issues',
  templateUrl: './issues.component.html',
  styleUrls: ['./issues.component.css'],
})
export class IssuesComponent implements OnInit {
  selectedIssuesCount = 0;
  issues: Issue[] = []
  constructor(
    private issuesService: IssuesService,
    private route: ActivatedRoute,
    private router: Router
    ) { }

  ngOnInit(): void {
    this.getIssues();
    this.getSelectedIssuesCount();
  }

  getIssues() {
    this.issuesService.getIssues().subscribe((issues) => {
      this.issues = issues;
    })
  }

  selectIssue(issue: Issue) {
    this.issuesService.addIssueToHistory(issue);
  }

  navigate() {
    this.router.navigate(["../selected"], {relativeTo: this.route})
  }

  getSelectedIssuesCount() {
    this.issuesService.issueHistorySubject.subscribe(x => this.selectedIssuesCount = x.length);
  }
}
