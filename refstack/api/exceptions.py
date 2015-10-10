#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Refstack API exceptions."""


class ParseInputsError(Exception):
    """Raise if input params are invalid."""

    pass


class ValidationError(Exception):
    """Raise if request doesn't pass trough validation process."""

    def __init__(self, title, exc=None):
        """Init."""
        super(ValidationError, self).__init__(title)
        self.exc = exc
        self.title = title
        self.details = "%s(%s: %s)" % (self.title,
                                       self.exc.__class__.__name__,
                                       str(self.exc)) \
            if self.exc else self.title

    def __repr__(self):
        """Repr method."""
        return self.details

    def __str__(self):
        """Str method."""
        return self.__repr__()
