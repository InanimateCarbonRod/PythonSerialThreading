class Parser():
    
    def add_bytes(self, data):
        #loop through the bytes to add and determine if they're valid to add at this time
        for c in data:
            #if part of a command has been received, add the character
            if len(self.__data_byte_list) > 0 and self.__data_byte_list[0] == self.__command_delimiter:
                self.__data_byte_list += [c]
            #if this character is the beginning of a command
            elif len(self.__data_byte_list) == 0 and c == self.__command_delimiter:
                self.__data_byte_list += [c]
            #otherwise, clear the array because there isn't a command forming yet
            else:
                self.__data_byte_list = []
            
            #if there's data in the list, see if it is a valid command
            if len(self.__data_byte_list) > 1:
                self.__is_valid()
                
        
    def __check(self):
        #a valid command starts with the command delimiter, followed by the # of following characters (length - 2)
        if self.__data_byte_list[0] == self.__command_delimiter:
            if len(self.__data_byte_list) == self.__data_byte_list[1] + 2:
                return True
        
        return False #__data_byte_list is invalid
    
    def __is_valid(self):
        if self.__check():
            #add the command to the list of parsed commands
            self.__parsed_commands.append(self.__data_byte_list)
            #clear the byte list because the command was valid
            self.__data_byte_list = []
            
    
    def pop(self):
        #return a command, or None if there are no remaining commands
        if len(self.__parsed_commands) >= 1:
            return self.__parsed_commands.pop(0)
        
        return None
    
    def count(self):
        return len(self.__parsed_commands)
        
            
    def __init__(self, command_delimiter = 0x44):
        self.__data_byte_list = []
        self.__parsed_commands = []
        self.__command_delimiter = command_delimiter
        
    
"""
def main():
    command_parser = Parser()
    
    command_parser.add_bytes([0x44, 0x02])
    command_parser.add_bytes([0x01, 0x00]) # these two lines should form one command
    command_parser.add_bytes([0x03, 0x44, 0x01, 0x01, 0x02]) #this should form a second command, 1st and last bytes are invalid and ignored
    command_parser.add_bytes([0x44, 0x02, 0x03, 0x04]) # forms a 3rd valid command
    
    print(command_parser.pop())
    print(command_parser.pop())
    print(command_parser.pop()) #3 commands should be printed from these 3 lines
    print(command_parser.pop()) #this should print "None"
    
if __name__ == '__main__':
    main()
"""
    