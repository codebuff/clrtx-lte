from collections import defaultdict
from collections import deque

class ClipBoard:
    def __init__(self):
        self.buffer = ""

    def get_content(self):
        return self.buffer

    def set_content(self, text):
        self.buffer = text

    def add_content(self, text):
        self.buffer += text


class Lte:
    def __init__(self):
        self.buffer = defaultdict(lambda: "\n")
        self.max_line_no = 0
        self.clipboard = ClipBoard()
        self.correct_usr_input = False
        self.undo_stack = []
        # self.redo_stack = []


    def print_msg(self):
        print("Welcome to line text editor\n")
        print("operation supported: \ndisplay \ninsert\ndelete\ncopy\npaste")
        print("undo operation is supported for insert and delete | copy and paste are not handled for undo")
        print("redo operation is not implemented")

    def get_buffer(self):
        return self.buffer

    def get_max_line_no(self):
        return self.max_line_no

    def set_max_line_no(self, line_no):
        self.max_line_no = line_no

    def get_clipboard(self):
        return self.clipboard

    def is_correct_input(self):
        return self.correct_usr_input

    def set_input_validity(self, validity):
        self.correct_usr_input = validity

    def add_to_undo(self, command):
        self.undo_stack.append(command)

    def get_undo(self):
        if self.undo_stack:
            return self.undo_stack.pop()
        else:
            return []
    #
    # def get_redo(self):
    #     if self.redo_stack:
    #         return self.redo_stack.pop()
    #     else:
    #         return []
    #
    # def add_to_redo(self, command):
    #     self.redo_stack.append(command)

    def shell(self):
        self.print_msg()
        while True:
            print("enter command")
            self.set_input_validity(False)
            user_cmd = input()
            cmd = user_cmd.strip().split()
            if not cmd:
                self.print_help(user_cmd)
                continue
            # dispaly operations
            if cmd[0] == "d":
                if len(cmd) == 1:
                    self.set_input_validity(True)
                    self.display_contents()
                elif len(cmd) == 3 and self.verify_line_nos(cmd[1], cmd[2]):
                    self.display_specific_lines(int(cmd[1]), int(cmd[2]))
                else:
                    self.print_help(user_cmd)
            # insert operations
            elif cmd[0] == 'i':
                if len(cmd) >= 3 and self.verify_line_nos(cmd[1], insert_cmd=True):
                    self.insert_line(int(cmd[1]), " ".join(cmd[2:]))
                else:
                    self.print_help(user_cmd)
            # delete operations
            elif cmd[0] == "dd":
                if len(cmd) == 2 and self.verify_line_nos(cmd[1]):
                    self.delete_line(int(cmd[1]))
                elif len(cmd) == 3 and self.verify_line_nos(cmd[1], cmd[2]):
                    self.delete_multiple_lines(int(cmd[1]), int(cmd[2]))
                else:
                    self.print_help(user_cmd)
            # copy operations
            elif cmd[0] == "yy":
                if len(cmd) == 3 and self.verify_line_nos(cmd[1], cmd[2]):
                    self.copy_multiple_lines(int(cmd[1]), int(cmd[2]))
                else:
                    self.print_help(user_cmd)
            # paste operations
            elif cmd[0] == "p":
                if len(cmd) == 2 and self.verify_line_nos(cmd[1]):
                    self.paste(int(cmd[1]))
                else:
                    self.print_help(user_cmd)
            elif cmd[0] == "z":
                if len(cmd) == 1:
                    self.set_input_validity(True)
                    self.undo()
                else:
                    self.print_help(user_cmd)
            elif cmd[0] == "zz":
                if len(cmd) == 1:
                    self.set_input_validity(True)
                    self.redo()
                else:
                    self.print_help()
            # add checks for any other operations here
            elif cmd[0] == "q":
                print("exiting...")
                break
            else:
                self.print_help(user_cmd)

    def verify_line_nos(self, start, end=None, insert_cmd=False):
        if end is None:
            try:
                temp = int(start)
                if insert_cmd:
                    self.set_input_validity(True)
                    return True
                if 1 <= temp <= self.get_max_line_no():
                    self.set_input_validity(True)
                    return True
                else:
                    self.print_help("invalid range")
                    return False
            except Exception as e:
                self.print_help(e)
                return False

        try:
            start = int(start)
            end = int(end)
            if 1 <= start < self.get_max_line_no() and 1 <= end <= self.get_max_line_no() and start <= end:
                self.set_input_validity(True)
                return True
            else:
                self.print_help(" invalid range")
                return False
        except Exception as e:
            self.print_help(e)
            return False

    def print_help(self, user_cmd):
        print("invalid command", user_cmd)
        # todo print list of command

    def display_contents(self):
        if not self.is_correct_input():
            return

        print(self.get_specific_lines(1, self.get_max_line_no()))

    def display_specific_lines(self, start, end):
        if not self.is_correct_input():
            return

        print(self.get_specific_lines(start, end))

    def get_specific_lines(self, start, end):
        if not self.is_correct_input():
            return

        string = ""
        buffer = self.get_buffer()
        for line_no in range(start, end+1):
            string += str(line_no) + ": " + buffer[line_no]
        return string

    def insert_line(self, insert_line_no, text, undo_op=False):
        if not self.is_correct_input():
            return

        buffer = self.get_buffer()
        if insert_line_no > self.get_max_line_no():
            if not undo_op:
                undo = []
                pos = self.get_max_line_no() + 1
                while pos < insert_line_no:
                    undo.append(["delete", pos])
                    pos += 1
                undo.append(["delete", insert_line_no])
                self.add_to_undo(undo)
            # else:
            #     self.add_to_redo([['insert', insert_line_no, text]])
            self.set_max_line_no(insert_line_no)
            if text[-1] != "\n":
                buffer[insert_line_no] = text + "\n"
            else:
                buffer[insert_line_no] = text
            return

        self.set_max_line_no(self.get_max_line_no() + 1)
        cur_line_no = self.get_max_line_no()

        while cur_line_no > insert_line_no:
            buffer[cur_line_no] = buffer[cur_line_no - 1]
            cur_line_no -= 1
        if text[-1] != "\n":
            buffer[insert_line_no] = text + "\n"
        else:
            buffer[insert_line_no] = text
        if not undo_op:
            self.add_to_undo([["delete", insert_line_no]])

    def delete_line(self, line_no, undo_op=False):
        if not self.is_correct_input():
            return

        self.delete_multiple_lines(line_no, line_no, undo_op)

    def delete_multiple_lines(self, start, end, undo_op=False):
        if not self.is_correct_input():
            return

        from_line_no = end + 1
        to_line_no = start
        buffer = self.get_buffer()
        if not undo_op:
            undo = []
            for pos in range(start, end+1):
                undo.append(["insert", pos, buffer[pos]])
            self.add_to_undo(undo)
        # else:
        #     redo = []
        #     for pos in range(start, end+1):
        #         redo.append(["delete", pos])
        #     self.add_to_redo(redo)
        while from_line_no <= self.get_max_line_no():
            buffer[to_line_no] = buffer[from_line_no]
            if from_line_no in buffer:
                del buffer[from_line_no]
            to_line_no += 1
            from_line_no += 1
        self.set_max_line_no(self.get_max_line_no() - (end-start + 1))
        while from_line_no > self.get_max_line_no():
            if from_line_no in buffer:
                del buffer[from_line_no]
            from_line_no -= 1

    def copy_multiple_lines(self, start, end):
        if not self.is_correct_input():
            return

        cb = self.get_clipboard()
        text  = []
        buffer = self.get_buffer()
        for line_no in range(start, end + 1):
            text.append(buffer[line_no])
        cb.set_content("".join(text))

    def paste(self, line_no):
        if not self.is_correct_input():
            return

        cb = self.get_clipboard()
        self.insert_line(line_no, cb.get_content())

    def undo(self):
        undo_op = self.get_undo()
        for op in undo_op:
            if op[0] == "delete":
                self.delete_line(op[1], undo_op=True)
            elif op[0] == "insert":
                self.insert_line(op[1], op[2], undo_op=True)

    def redo(self):
        print("not implemented")
        return
        # redo_op = self.get_redo()
        # for op in redo_op:
        #     if op[0] == "delete":
        #         self.delete_line(op[1])
        #     elif op[0] == "insert":
        #         self.insert_line(op[1], op[2])


if __name__ == "__main__":
    lte = Lte()
    #lte.set_max_line_no(100)
    lte.shell()



# todo call verification in function also
