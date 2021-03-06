"""
###########################################################################
File: undo_redo.py
Author:
Description: Undo/Redo module for recording and setting the previous state of significant
            user actions.


Copyright (C) PyMerge Team 2019

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
###########################################################################
"""

"""
Undo function can be implemented by keeping a buffer of each state change. That is, each time a change is made, 
the row state is  copied to a list containing the last n number of row copies. If undo is selected, the 
undo index is recorded and that copy of the row state is used to replace the current working version. The current working version
is then copied to a redo buffer. 
"""


class Stack(object):
    def __init__(self, stack_size: int):
        self._max_size: int = 0
        self.stack = []

        self.max_size = stack_size

    @property
    def max_size(self) -> int:
        return self._max_size

    @max_size.setter
    def max_size(self, value: int):
        self._max_size = value

    def stack_push(self, item):
        # Check if stack is full, then append the object onto the end
        if len(self.stack) < self.max_size or self.max_size == -1:
            self.stack.append(item)
            
        else:
            self._rotate()
            self.stack[-1] = item

    def _rotate(self):
        # Move the stack up, "forgetting" the oldest undo or redo move
        for n in range(1, len(self.stack)):
            self.stack[n - 1] = self.stack[n]

    def stack_pop(self):
        # Check if stack is empty, then pop the top object
        # return self.stack.pop()
        if len(self.stack) > 0:
            return self.stack.pop()
        return None

    def _size(self):
        return len(self.stack)


class UndoRedoAction(object):
    __slots__ = ["obj_copy", "obj_ref",]

    def __init__(self, record_obj):
        self.obj_copy = record_obj.__dict__.copy()
        self.obj_ref = record_obj

    def set_state(self):
        """
        Set the current state of the row object to what was recorded in the instance variables
        :return: No return value
        """
        # Copy the copied attribute dictionary over to the object reference        
        for key in self.obj_ref.__dict__:
            if self.obj_ref.right_button.isEnabled():
                self.obj_ref.right_button.setEnabled(False)
                self.obj_ref.left_button.setEnabled(False)
            else:
                self.obj_ref.right_button.setEnabled(True)
                self.obj_ref.left_button.setEnabled(True)

            try:
                self.obj_ref.__dict__[key] = self.obj_copy[key]
            except KeyError:
                print(f"Attribute '{key}' not found!")
                pass


class UndoRedo(object):
    _instance = None    # Holds the single instance of this class
    MAX_BUF_SIZE = 400  # Hard upper limit for maximum undo/redo buffer size

    def __init__(self, buf_size: int):
        if UndoRedo._instance is not None:
            raise Exception("Only a single instance of UndoRedo is allowed!")
        else:
            self._redo_buf = Stack(buf_size)
            self._undo_buf = Stack(buf_size)
            self.undo_buf_size = 0
            self._buf_size = buf_size            
            UndoRedo._instance = self

    @staticmethod
    def get_instance(buf_size=200):
        if UndoRedo._instance is None:
            UndoRedo(buf_size)
        return UndoRedo._instance

    @property
    def buf_size(self) -> int:
        return self._buf_size

    @buf_size.setter
    def buf_size(self, value: int):
        if value <= 0:
            self._buf_size = 0
        elif value >= self.MAX_BUF_SIZE:
            self._buf_size = self.MAX_BUF_SIZE
        else:
            self._buf_size = value

    def record_action(self, record_obj):
        """
        Record the state of a class/object and push onto stack.
        """
        self._undo_buf.stack_push(UndoRedoAction(record_obj))

    def undo(self) -> bool:
        """
        Pops an UndoRedoAction from the stack and sets the state of its referenced
        object.
        """
        undo_obj: UndoRedoAction = self._undo_buf.stack_pop()  # Get the state we want to set
        
        # Check if object is None, then push the recorded current state.
        if undo_obj is not None:
            self._redo_buf.stack_push(UndoRedoAction(undo_obj.obj_ref))        
            # Restore the state to what was popped
            undo_obj.set_state()
            return True
        return False

    def redo(self) -> bool:
        redo_obj: UndoRedoAction = self._redo_buf.stack_pop()

        # Check if object is None, then push the recorded current state.
        if redo_obj is not None:
            self._undo_buf.stack_push(UndoRedoAction(redo_obj.obj_ref))

            # Restore the state to what was popped
            redo_obj.set_state()
            return True
        return False
