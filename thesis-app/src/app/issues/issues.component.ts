import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
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
  issues: Issue[] = [];
  pageNumber: number = 1;
  pageSize: number = 10;
  totalCount: number = 0;
  queryString: string = "";

  constructor(
    private issuesService: IssuesService,
    private route: ActivatedRoute,
    private router: Router,
    private _snackBar: MatSnackBar
    ) { }

  ngOnInit(): void {
    this.getIssues();
    this.getIssuesCount();
    this.getSelectedIssuesCount();
  }

  openSnackBar() {
    this._snackBar.open("Issue assigned", "Dismiss", {duration: 2000});
  }

  getIssues() {
    let params = {
      pageNumber: this.pageNumber,
      pageSize: this.pageSize,
      queryString: this.queryString
    }
    this.issuesService.getIssues(params).subscribe((issues) => {
      this.issues = issues;
    })
  }

  getIssuesCount() {
    this.issuesService.getIssuesCount({queryString:this.queryString}).subscribe(x => this.totalCount = x)
  }

  selectIssue(issue: Issue) {
    this.issuesService.addIssueToHistory(issue);
    this.openSnackBar();
  }

  navigate() {
    this.router.navigate(["../selected"], {relativeTo: this.route})
  }

  getSelectedIssuesCount() {
    this.issuesService.issueHistorySubject.subscribe(x => this.selectedIssuesCount = x.length);
  }

  search() {
    this.getIssues();
    this.getIssuesCount();
  }

  pageChanged($event: any) {
    this.pageSize = $event.pageSize;
    this.pageNumber = $event.pageIndex + 1;
    this.getIssues();
    this.getIssuesCount();
  }
}
