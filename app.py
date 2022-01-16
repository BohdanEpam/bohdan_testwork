#!/usr/bin/env python3
import os

import aws_cdk as cdk

from announcements.announcements_stack import AnnouncementsStack


app = cdk.App()
AnnouncementsStack(app, "AnnouncementsStack")

app.synth()
