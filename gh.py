#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @File: gh.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Thu Aug 24 09:45:00 CST 2023
#
import configparser
import cmd
import json
import shlex

from subprocess import Popen, check_output
from string import Template

cmd_query_discussions = Template('''
gh api graphql -F owner='{owner}' -F name='{repo}' -f query='
  query($$name: String!, $$owner: String!) {
    repository(owner: $$owner, name: $$name) {
      discussions(first: $nd) {
        nodes {
          id
          number
          title
          updatedAt
          bodyText
          comments (last: $nc) {
            nodes {
              id
              publishedAt
              lastEditedAt
              body
              replies (last: $nc) {
                nodes {
                  id
                  publishedAt
                  body
                }
              }
            }
          }
        }
      }
    }
  }'
''')

discussion_list_template = Template('''
$num $updatedAt $discussionId
$title
''')

discussion_template = Template('''
$num $updatedAt $discussionId
$title
==========================================
$body
$comments
''')

discussion_comment_template = Template('''
------------------------------------------
$publishedAt $commentId
$body
$replies''')

reply_comment_template = Template('''
$publishedAt $commentId
$body''')

cmd_list_discussions = Template('''
gh api graphql -F owner='{owner}' -F name='{repo}' -f query='
  query($$name: String!, $$owner: String!) {
    repository(owner: $$owner, name: $$name) {
      discussions(first: $nd) {
        nodes {
          id
          number
          title
          updatedAt
        }
      }
    }
  }' --template '{{range .data.repository.discussions.nodes}}
{{.number}} {{.updatedAt}} {{.id}}
{{.title}}
{{end}}
'
''')

cmd_view_discussion = Template('''
gh api graphql -F owner='{owner}' -F name='{repo}' -f query='
  query($$name: String!, $$owner: String!) {
    repository(owner: $$owner, name: $$name) {
      discussions(first: $nd) {
        nodes {
          id
          number
          title
          updatedAt
          bodyText
          comments (last: $nc) {
            nodes {
              id
              publishedAt
              lastEditedAt
              body
            }
          }
        }
      }
    }
  }' --template '{{range .data.repository.discussions.nodes}}
{{"============================"}}
{{.number}} {{.updatedAt}} {{.id}}
{{.title}}
{{.bodyText}}
{{range .comments.nodes}}
{{"----------------------------"}}
{{.publishedAt}} {{.id}}
{{.body}}
{{end}}
{{end}}
'
''')

cmd_add_discussion_comment = Template('''
gh api graphql -f query='
  mutation {
    addDiscussionComment(input: {
      discussionId: "$discussionId",
      body: "$body"
    }) {
      clientMutationId
      comment {
        id
      }
    }
  }'
''')

cmd_discussion_graphql = 'gh api graphql'

query_add_discussion_comment = Template('''
  mutation {
    addDiscussionComment(input: {
      discussionId: "$discussionId",
      body: "$body"
    }) {
      clientMutationId
      comment {
        id
      }
    }
  }
''')

query_update_discussion_comment = Template('''
  mutation {
    updateDiscussionComment(input: {
      commentId: "$commentId",
      body: "$body"
    }) {
      clientMutationId
      comment {
        id
      }
    }
  }
''')

cmd_delete_discussion_comment = Template('''
gh api graphql -f query='
  mutation {
    deleteDiscussionComment(input: {
      id: "$commentId"
    }) {
      clientMutationId
      comment {
        id
        bodyText
      }
    }
  }'
''')

cmd_delete_discussion = Template('''
gh api graphql -f query='
  mutation {
    deleteDiscussion(input: {
      id: "$nodeId"
    }) {
      clientMutationId
      discussion {
        id
        title
      }
    }
  }'
''')

cmd_list_issues = Template('''
gh issue list --search "sort:updated"
''')

cmd_view_issue = Template('''
gh issue view $issueId $options
''')

cmd_close_issue = Template('''
gh issue close $issueId
''')

cmd_label_issue = Template('''
gh issue edit $issueId --add-label "$label" --remove-label bug
''')

cmd_comment_issue = Template('''
gh issue comment $issueId -e
''')

cmd_last_comment_issue = Template('''
gh issue comment $issueId --edit-last
''')

cmd_list_notifications = Template('''
gh api notifications --template '{{range .}}
{{.id}} {{.reason}} {{.subject.type}} {{.updated_at}}
{{.subject.url}}
{{.subject.title}}
{{end}}
'
''')

cmd_mark_notification = Template('''
gh api --method PATCH /notifications/threads/$threadId
''')

cmd_mark_all_notification = Template('''
gh api --method PUT /repos/dashingsoft/pyarmor/notifications \
  -f last_read_at='$timestamp'
''')

cmd_view_issue_raw_body = Template('''
gh issue view $issueId --json title,body --template "
{{.title}}
{{.body}}"
''')

cmd_view_issue_raw_comments = Template('''
gh issue view $issueId -c --json title,body,comments --template "
{{.title}}
{{.body}}
{{.comments}}
"
''')


def call_cmd(cmd):
    Popen(cmd.strip(), shell=True).wait()
    # args = shlex.split(cmd)
    # Popen(args).wait()


def call_query(cmd, query):
    args = shlex.split(cmd)
    args.extend(['-f', "query='%s'" % shlex.quote(query).strip("'")])
    Popen(' '.join(args), shell=True).wait()


def read_body(prompt):
    lines = []

    try:
        s = input(prompt + '\n')
        while s not in ('EOF', 'e'):
            if not s:
                print()
            lines.append(s)
            s = input()
    except KeyboardInterrupt:
        lines.clear()
        print('Abort by user, there is nothing to do')

    return '\n'.join(lines)


class Github(cmd.Cmd):

    intro = 'Welcome to Github cli shell. Type help or ? to list commands.\n'
    prompt = '(github) '

    n_discussion = 5
    n_discussion_comment = 3

    def __init__(self):
        super().__init__()
        self.cfg = configparser.ConfigParser(
            empty_lines_in_values=False,
            interpolation=configparser.ExtendedInterpolation(),
        )

        self.discussions = None
        self.issueId = None
        self.discussionId = None

    def do_exit(self, arg):
        'Finish and exit'
        print('Thank you for using Github cli')
        return True
    do_EOF = do_q = do_exit

    def do_close(self, arg):
        'Close issues'
        call_cmd(cmd_close_issue.substitute(issueId=arg))

    def do_rn(self, arg):
        'Mark notification readed'
        if arg in ('all', '*'):
            from datetime import datetime
            now = datetime.now().isoformat()
            call_cmd(cmd_mark_all_notification.substitute(timestamp=now))
        else:
            for tid in arg.split():
                print('mark thread %s as readed' % tid)
                call_cmd(cmd_mark_notification.substitute(threadId=tid))

    def do_li(self, arg):
        '''List issues'''
        call_cmd(cmd_list_issues.substitute())
    do_l = do_li

    def do_ld(self, arg):
        '''List discussions'''
        nd = int(arg) if arg else self.n_discussion
        # call_cmd(cmd_list_discussions.substitute(nd=nd))
        nc = self.n_discussion_comment
        cmd = cmd_query_discussions.substitute(nd=nd, nc=nc)
        res = check_output(shlex.split(cmd))
        try:
            self.discussions = json.loads(res)['data']['repository']
        except Exception as e:
            print('error:', e)
        else:
            lines = []
            for node in self.discussions['discussions']['nodes']:
                lines.append(discussion_list_template.substitute(
                    num=node['number'],
                    discussionId=node['id'],
                    title=node['title'],
                    updatedAt=node['updatedAt']))
            print(''.join(lines))

    def do_ln(self, arg):
        '''List notifitions'''
        call_cmd(cmd_list_notifications.substitute())

    def do_vi(self, arg):
        'View issue'
        paras = arg.split(' ', 1)
        issueId = int(paras[0])
        options = ' '.join(paras[1:])
        call_cmd(cmd_view_issue.substitute(issueId=issueId, options=options))
        self.issueId = issueId
    do_v = do_vi

    def do_vd(self, arg):
        'View discussion'
        lines = []
        for node in self.discussions['discussions']['nodes']:
            if arg and int(arg) != node['number']:
                continue
            self.discussionId = node['id']
            comments = []
            for cnode in node['comments']['nodes']:
                replies = []
                for rnode in cnode['replies']['nodes']:
                    replies.append(reply_comment_template.substitute(
                        commentId=rnode['id'],
                        publishedAt=rnode['publishedAt'],
                        body=rnode['body']))
                comments.append(discussion_comment_template.substitute(
                    commentId=cnode['id'],
                    publishedAt=cnode['publishedAt'],
                    body=cnode['body'],
                    replies=''.join(replies)))
            lines.append(discussion_template.substitute(
                num=node['number'],
                discussionId=node['id'],
                title=node['title'],
                updatedAt=node['updatedAt'],
                body=node['bodyText'],
                comments=''.join(comments)))
        print(''.join(lines))

    def do_ac(self, arg):
        'Add issue comment'
        issueId = arg if arg else self.issueId
        call_cmd(cmd_comment_issue.substitute(issueId=issueId))
        self.issueId = issueId

    def do_uc(self, arg):
        'Update issue last comment'
        issueId = arg if arg else self.issueId
        call_cmd(cmd_last_comment_issue.substitute(issueId=issueId))
        self.issueId = issueId

    def _find_discussion(self, arg):
        for node in self.discussions['discussions']['nodes']:
            if arg:
                if int(arg) == node['number']:
                    self.discussionId = node['id']
                    return node
            elif self.discussionId == node['id']:
                return node

    def do_ad(self, arg):
        'Add discussion comment'
        node = self._find_discussion(arg)
        if node:
            print(node['number'], node['title'])
            discussionId = node['id']

            body = read_body('Add discussion comment:')
            if body:
                query = query_add_discussion_comment.substitute(
                    discussionId=discussionId,
                    body=body.replace('"', r'\"'))
                call_query(cmd_discussion_graphql, query)

    def do_dd(self, arg):
        'Delete discussion comment'
        call_cmd(cmd_delete_discussion_comment.substitute(commentId=arg))

    def do_ud(self, arg):
        'Update discussion comment'
        oldBody = None
        for node in self.discussions['discussions']['nodes']:
            for cnode in node['comments']['nodes']:
                if cnode['id'] == arg:
                    oldBody = cnode['body']
                    break
            if oldBody:
                break
        else:
            print('No comment found, do nothing')

        print('Original issue comment:')
        print()
        print(oldBody)
        print()

        body = oldBody
        while True:
            pat = input('Replace: ')
            if not pat:
                break
            s = input('with : ')
            body = body.replace(pat, s)

        print()
        if body == oldBody:
            print('There is no changes, do thing')
        else:
            print('Updated comment:')
            print()
            print(body)
            print()
            if input('Are you sure (y/n) : ') in ('', 'y', 'Y'):
                query = query_update_discussion_comment.substitute(
                    commentId=arg,
                    body=body.replace('"', r'\"'))
                call_query(cmd_discussion_graphql, query)

    def do_cii(self, arg):
        'Quickly close issue by marked as documented or invalid'
        if arg.find(' ') == -1:
            issueId, label = arg, 'invalid'
        else:
            issueId, label = arg.split()
            if label in ('d', 'doc'):
                label = 'documented'
            elif label in ('w', 'wrong'):
                label = 'wrong usage'
        if label not in ('documented', 'invalid', 'wrong usage'):
            print('invalid label "%s"' % label)
            return
        call_cmd(cmd_label_issue.substitute(issueId=issueId, label=label))
        call_cmd(cmd_close_issue.substitute(issueId=issueId))

    def do_shell(self, arg):
        'Execute shell command'
        call_cmd(arg)


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))


if __name__ == '__main__':
    Github().cmdloop()
