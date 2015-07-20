#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import string
import random


def random_string_generator(size=64, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))